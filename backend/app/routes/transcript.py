from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import uuid4

from app.services.question_judge import validate_question
from app.database import get_db
from app.models.dialogue import Dialogue
from sqlalchemy.orm import Session
from app.utils.logger import logger, log_db_operation
router = APIRouter()


class TranscriptRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="识别出的文本")
    session_id: Optional[str] = Field(None, description="会话ID，用于区分不同浏览器会话")


class TranscriptResponse(BaseModel):
    code: int
    message: str
    data: Optional[Dict] = None


class DialogueItem(BaseModel):
    id: str
    question: str
    answer: str
    is_valid: bool
    rule: str
    created_at: str


@router.post("/transcript", response_model=TranscriptResponse)
async def process_transcript(req: TranscriptRequest, db: Session = Depends(get_db)):
    """接收前端识别的文本，进行问题判断"""
    logger.info(f"收到识别文本: {req.text[:50]}...")

    validation = validate_question(req.text)

    if not validation['is_valid']:
        logger.info(f"问题判断跳过: {validation['reason']}")
        return {
            'code': 0,
            'message': '已接收',
            'data': {
                'is_valid': False,
                'reason': validation['reason']
            }
        }

    session_id = req.session_id or str(uuid4())
    dialogue_id = f"dialogue_{uuid4().hex[:8]}"
    now = datetime.now().isoformat()

    dialogue = Dialogue(
        id=dialogue_id,
        session_id=session_id,
        question=req.text.strip(),
        answer='等待大模型接入...',
        is_valid=True,
        rule=validation['rule']
    )

    db.add(dialogue)
    db.commit()
    db.refresh(dialogue)

    log_db_operation("INSERT", "dialogues", True, f"有效问题已添加: {dialogue_id}, session: {session_id}")

    return {
        'code': 0,
        'message': 'success',
        'data': {
            'id': dialogue.id,
            'question': dialogue.question,
            'answer': dialogue.answer,
            'is_valid': dialogue.is_valid,
            'rule': dialogue.rule,
            'created_at': dialogue.created_at.isoformat() if dialogue.created_at else now,
            'session_id': session_id
        }
    }


@router.get("/dialogues", response_model=TranscriptResponse)
async def get_dialogues(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """获取当前会话的所有对话记录"""
    query = db.query(Dialogue)
    if session_id:
        query = query.filter(Dialogue.session_id == session_id)
    
    dialogues = query.order_by(Dialogue.created_at).all()

    result = []
    for d in dialogues:
        result.append({
            'id': d.id,
            'question': d.question,
            'answer': d.answer,
            'is_valid': d.is_valid,
            'rule': d.rule,
            'created_at': d.created_at.isoformat() if d.created_at else '',
            'session_id': d.session_id
        })

    return {
        'code': 0,
        'message': 'success',
        'data': {
            'dialogues': result
        }
    }


@router.delete("/dialogues", response_model=TranscriptResponse)
async def clear_dialogues(session_id: Optional[str] = None, db: Session = Depends(get_db)):
    """清空对话记录"""
    query = db.query(Dialogue)
    if session_id:
        query = query.filter(Dialogue.session_id == session_id)
    
    count = query.delete()
    db.commit()

    log_db_operation("DELETE", "dialogues", True, f"对话记录已清空: {count} 条, session: {session_id}")
    return {
        'code': 0,
        'message': f'成功删除 {count} 条记录'
    }


@router.put("/dialogues/{dialogue_id}", response_model=TranscriptResponse)
async def update_dialogue(
    dialogue_id: str,
    answer: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """更新对话记录（主要用于更新回答）"""
    dialogue = db.query(Dialogue).filter(Dialogue.id == dialogue_id).first()
    
    if not dialogue:
        raise HTTPException(status_code=404, detail="对话记录不存在")

    if answer is not None:
        dialogue.answer = answer
    
    db.commit()
    db.refresh(dialogue)

    log_db_operation("UPDATE", "dialogues", True, f"对话记录已更新: {dialogue_id}")
    return {
        'code': 0,
        'message': 'success',
        'data': {
            'id': dialogue.id,
            'question': dialogue.question,
            'answer': dialogue.answer,
            'is_valid': dialogue.is_valid,
            'rule': dialogue.rule,
            'created_at': dialogue.created_at.isoformat() if dialogue.created_at else ''
        }
    }
