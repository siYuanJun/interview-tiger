import os
import uuid
import shutil
from typing import Optional, List, Dict, Any
from pathlib import Path

from app.utils.logger import logger, log_api_error
from config import (
    LOCAL_KB_DATA_DIR,
    LOCAL_KB_ORIGINALS_DIR,
    LOCAL_KB_EMBEDDING_MODEL,
    LOCAL_KB_CHUNK_SIZE,
    LOCAL_KB_CHUNK_OVERLAP,
    HYBRID_ENABLED,
    QUERY_EXPAND_ENABLED,
    VALIDATOR_ENABLED,
    SESSION_MEMORY_ENABLED,
)

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader,
    JSONLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document


class LocalKnowledgeProvider:
    _instance = None
    _vector_store = None
    _embeddings = None

    def __init__(self):
        self.data_dir = Path(LOCAL_KB_DATA_DIR)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._init_embeddings()
        self._init_vector_store()

        # RAG 3.0 模块（延迟初始化）
        self._hybrid_retriever = None
        self._query_rewriter = None
        self._memory = None
        self._validator = None
        self._init_rag3_modules()

    def _init_embeddings(self):
        try:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=LOCAL_KB_EMBEDDING_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True}
            )
            logger.info(f"Embedding模型加载成功: {LOCAL_KB_EMBEDDING_MODEL}")
        except Exception as e:
            log_api_error("init_embeddings", e, {"model": LOCAL_KB_EMBEDDING_MODEL})
            raise

    def _init_vector_store(self):
        try:
            self._vector_store = Chroma(
                persist_directory=str(self.data_dir),
                embedding_function=self._embeddings,
                collection_name="interview_tiger_kb"
            )
            logger.info(f"ChromaDB初始化成功，数据目录: {self.data_dir}")
        except Exception as e:
            log_api_error("init_vector_store", e, {"data_dir": str(self.data_dir)})
            raise

    def _init_rag3_modules(self):
        """延迟初始化 RAG 3.0 模块（非关键，失败不影响服务）"""
        # Query Rewriter（零依赖，始终可用）
        if QUERY_EXPAND_ENABLED:
            try:
                from app.services.query_rewriter import QueryRewriter
                self._query_rewriter = QueryRewriter()
                logger.info("[RAG3] QueryRewriter 初始化成功")
            except Exception as e:
                logger.warning(f"[RAG3] QueryRewriter 初始化失败: {e}")

        # Session Memory（零依赖，始终可用）
        if SESSION_MEMORY_ENABLED:
            try:
                from app.services.memory import SessionMemory
                self._memory = SessionMemory()
                logger.info("[RAG3] SessionMemory 初始化成功")
            except Exception as e:
                logger.warning(f"[RAG3] SessionMemory 初始化失败: {e}")

        # Validator（依赖 LLM API）
        if VALIDATOR_ENABLED:
            try:
                from app.services.validator import ContentValidator
                self._validator = ContentValidator()
                if self._validator.is_enabled():
                    logger.info("[RAG3] ContentValidator 初始化成功")
                else:
                    logger.info("[RAG3] ContentValidator 禁用（无 API Key）")
            except Exception as e:
                logger.warning(f"[RAG3] ContentValidator 初始化失败: {e}")

        # Hybrid Retriever（依赖 BM25 索引，需全量文档）
        self._rebuild_hybrid()

    def _get_all_documents(self) -> list:
        """获取全量文档列表（用于 BM25 索引构建）"""
        try:
            if self._vector_store is None:
                return []
            collection = self._vector_store._collection
            if collection is None:
                return []
            results = collection.get(include=['documents', 'metadatas'])
            docs = []
            for i, content in enumerate(results.get('documents', [])):
                metadata = results['metadatas'][i] if i < len(results.get('metadatas', [])) else {}
                docs.append(Document(page_content=content, metadata=metadata))
            return docs
        except Exception as e:
            logger.warning(f"[RAG3] 获取全量文档失败: {e}")
            return []

    def _rebuild_hybrid(self):
        """重建混合检索器（文档变更后调用）"""
        if not HYBRID_ENABLED:
            self._hybrid_retriever = None
            return
        try:
            from app.services.hybrid_retriever import HybridRetriever
            all_docs = self._get_all_documents()
            if all_docs and self._vector_store:
                self._hybrid_retriever = HybridRetriever(self._vector_store, all_docs)
            else:
                self._hybrid_retriever = None
                logger.debug("[RAG3] HybridRetriever 跳过（无文档）")
        except Exception as e:
            logger.warning(f"[RAG3] HybridRetriever 初始化失败: {e}")
            self._hybrid_retriever = None

    def _get_loader(self, file_path: str):
        ext = file_path.lower().split('.')[-1]
        if ext == 'pdf':
            return PyPDFLoader(file_path)
        elif ext in ['txt', 'md', 'markdown']:
            return TextLoader(file_path, encoding='utf-8')
        elif ext == 'docx':
            return Docx2txtLoader(file_path)
        elif ext == 'json':
            return JSONLoader(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    def search(self, query: str, **kwargs) -> str:
        """RAG 3.0 混合检索管线: QueryExpand → Hybrid → Validate → Memory"""
        try:
            top_k = kwargs.get('top_k', 3)
            session_id = kwargs.get('session_id', '')
            if self._vector_store is None:
                return ""

            # P2: 会话记忆 — 跟进问题复用缓存
            if self._memory and session_id:
                if self._memory.is_follow_up(session_id, query):
                    cached = self._memory.get(session_id)
                    if cached and cached.get("kb_results"):
                        logger.info(f"[Memory] 跟进问题命中缓存: {query[:30]}")
                        return cached["kb_results"]

            # P0: Query 扩展
            queries = [query]
            if self._query_rewriter:
                queries = self._query_rewriter.expand(query)
                if len(queries) > 1:
                    logger.debug(f"[Rewriter] 扩展为 {len(queries)} 个查询变体")

            # P0: 混合检索（BM25 + Dense + RRF）
            all_chunks = []
            seen = set()
            for q in queries:
                if self._hybrid_retriever and self._hybrid_retriever.is_ready():
                    docs = self._hybrid_retriever.search(q, top_k=top_k * 2)
                else:
                    # 降级：纯向量检索
                    results = self._vector_store.similarity_search_with_score(
                        query=q, k=top_k * 2
                    )
                    docs = [doc for doc, score in results if score >= 0.3]

                for doc in docs:
                    content = doc.page_content
                    if content and content not in seen:
                        all_chunks.append(content)
                        seen.add(content)

                if len(all_chunks) >= top_k:
                    break

            if not all_chunks:
                return ""

            # P1: Validator — LLM 过滤无关片段
            validated = all_chunks
            if self._validator and self._validator.is_enabled():
                validated = self._validator.validate(query, all_chunks[:top_k * 2])
                if not validated:
                    validated = all_chunks[:top_k]  # 校验全过滤时保留前 K

            # 最终拼接
            knowledge_str = '\n'.join(validated[:top_k])

            # P2: 缓存结果
            if self._memory and session_id and knowledge_str:
                self._memory.set(session_id, query, knowledge_str)

            return knowledge_str

        except Exception as e:
            log_api_error("local_kb_search", e, {"query": query[:30]})
            return ""

    def search_with_details(self, query: str, **kwargs) -> Dict[str, Any]:
        try:
            top_k = kwargs.get('top_k', 5)
            if self._vector_store is None:
                return {"chunks": []}

            # 使用混合检索（如果有）
            if self._hybrid_retriever and self._hybrid_retriever.is_ready():
                docs = self._hybrid_retriever.search(query, top_k=top_k)
            else:
                results = self._vector_store.similarity_search_with_score(
                    query=query, k=top_k
                )
                docs = [doc for doc, _ in results]

            chunks = []
            for doc in docs[:top_k]:
                content = doc.page_content
                if content:
                    chunks.append({
                        "content": content,
                        "doc_name": doc.metadata.get('source', '本地文档'),
                        "doc_id": doc.metadata.get('doc_id', '')
                    })

            return {"chunks": chunks}
        except Exception as e:
            log_api_error("local_kb_search_with_details", e, {"query": query[:30]})
            return {"chunks": []}

    def upload(self, files, **kwargs) -> Dict[str, Any]:
        try:
            chunk_size = kwargs.get('chunk_size', LOCAL_KB_CHUNK_SIZE)
            chunk_overlap = kwargs.get('chunk_overlap', LOCAL_KB_CHUNK_OVERLAP)
            
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""]
            )

            all_docs = []
            uploaded_files = []

            for file in files:
                temp_path = f"/tmp/{uuid.uuid4().hex}_{file.filename}"
                # 只读取一次文件内容写入临时文件
                file_content = file.file.read()
                with open(temp_path, 'wb') as f:
                    f.write(file_content)

                try:
                    loader = self._get_loader(temp_path)
                    docs = loader.load()
                    
                    for doc in docs:
                        doc.metadata['doc_id'] = str(uuid.uuid4())
                        doc.metadata['source'] = file.filename
                        doc.metadata['file_size'] = os.path.getsize(temp_path)

                    split_docs = text_splitter.split_documents(docs)
                    all_docs.extend(split_docs)
                    
                    uploaded_files.append({
                        "filename": file.filename,
                        "doc_id": docs[0].metadata['doc_id'] if docs else "",
                        "chunks": len(split_docs)
                    })

                    logger.info(f"文件上传成功: {file.filename}, 切片数: {len(split_docs)}")
                except Exception as e:
                    logger.error(f"文件处理失败: {file.filename}, 错误: {str(e)}")
                finally:
                    # 持久化原始文件到 originals 目录
                    originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
                    originals_dir.mkdir(parents=True, exist_ok=True)
                    if docs:
                        doc_id = docs[0].metadata['doc_id']
                        persistent_path = originals_dir / f"{doc_id}_{file.filename}"
                        shutil.copy2(temp_path, persistent_path)
                    if os.path.exists(temp_path):
                        os.remove(temp_path)

            if all_docs:
                self._vector_store.add_documents(all_docs)
                self._vector_store.persist()
                self._rebuild_hybrid()  # RAG3: 重建 BM25 索引
                logger.info(f"共上传 {len(all_docs)} 个切片")

            return {
                "code": 0,
                "message": f"成功上传 {len(uploaded_files)} 个文件",
                "data": uploaded_files
            }
        except Exception as e:
            log_api_error("local_kb_upload", e, {"file_count": len(files)})
            return {
                "code": -1,
                "message": f"上传失败: {str(e)}",
                "data": []
            }

    def list_docs(self) -> List[Dict[str, Any]]:
        try:
            if self._vector_store is None:
                return []

            collection = self._vector_store._collection
            if collection is None:
                return []

            results = collection.get(include=['metadatas'])
            metadatas = results.get('metadatas', [])
            
            doc_map = {}
            for metadata in metadatas:
                source = metadata.get('source', '未知文档')
                if source not in doc_map:
                    doc_map[source] = {
                        "doc_name": source,
                        "doc_id": metadata.get('doc_id', ''),
                        "chunks": 0,
                        "file_size_bytes": metadata.get('file_size', 0)
                    }
                doc_map[source]["chunks"] += 1

            return list(doc_map.values())
        except Exception as e:
            log_api_error("local_kb_list_docs", e, {})
            return []

    def delete_doc(self, doc_id: str) -> Dict[str, Any]:
        try:
            if self._vector_store is None:
                return {"code": -1, "message": "向量库未初始化", "data": {}}

            collection = self._vector_store._collection
            if collection is None:
                return {"code": -1, "message": "集合不存在", "data": {}}

            results = collection.get(include=['metadatas'])
            ids_to_delete = []
            doc_name = ""
            
            for idx, metadata in enumerate(results.get('metadatas', [])):
                if metadata.get('doc_id') == doc_id:
                    ids_to_delete.append(results['ids'][idx])
                    doc_name = metadata.get('source', '')

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                self._vector_store.persist()
                self._rebuild_hybrid()  # RAG3: 重建 BM25 索引
                # 同步删除原始文件
                originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
                for f in originals_dir.glob(f"{doc_id}_*"):
                    f.unlink()
                    logger.info(f"已删除原始文件: {f.name}")
                return {
                    "code": 0,
                    "message": f"成功删除文档: {doc_name}",
                    "data": {"doc_id": doc_id, "chunks_deleted": len(ids_to_delete)}
                }
            else:
                return {"code": -1, "message": "未找到指定文档", "data": {}}
        except Exception as e:
            log_api_error("local_kb_delete_doc", e, {"doc_id": doc_id})
            return {"code": -1, "message": f"删除失败: {str(e)}", "data": {}}

    def clear(self) -> Dict[str, Any]:
        try:
            if self._vector_store is None:
                return {"code": -1, "message": "向量库未初始化", "data": {}}

            collection = self._vector_store._collection
            if collection is None:
                return {"code": -1, "message": "集合不存在", "data": {}}

            results = collection.get()
            ids = results.get('ids', [])
            total_chunks = len(ids)
            
            if ids:
                collection.delete(ids=ids)
                self._vector_store.persist()
                self._rebuild_hybrid()  # RAG3: 重建 BM25 索引
            # 清空原始文件目录
            originals_dir = Path(LOCAL_KB_ORIGINALS_DIR)
            if originals_dir.exists():
                shutil.rmtree(originals_dir)
                originals_dir.mkdir(parents=True, exist_ok=True)
                logger.info("已清空原始文件目录")

            return {
                "code": 0,
                "message": f"已清空 {total_chunks} 个切片",
                "data": {"chunks_deleted": total_chunks}
            }
        except Exception as e:
            log_api_error("local_kb_clear", e, {})
            return {"code": -1, "message": f"清空失败: {str(e)}", "data": {}}

    def get_stats(self) -> Dict[str, Any]:
        try:
            if self._vector_store is None:
                return {"code": -1, "message": "向量库未初始化", "data": {}}

            collection = self._vector_store._collection
            if collection is None:
                return {"code": -1, "message": "集合不存在", "data": {}}

            count = collection.count()
            return {
                "code": 0,
                "message": "success",
                "data": {
                    "total_chunks": count,
                    "data_dir": str(self.data_dir),
                    "embedding_model": LOCAL_KB_EMBEDDING_MODEL
                }
            }
        except Exception as e:
            log_api_error("local_kb_stats", e, {})
            return {"code": -1, "message": f"获取统计失败: {str(e)}", "data": {}}
