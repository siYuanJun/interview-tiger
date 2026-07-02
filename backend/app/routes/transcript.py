import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from app.services.question_judge import validate_question

logger = logging.getLogger("interview-tiger")
router = APIRouter()

dialogues: List[Dict] = []


class TranscriptRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, description="识别出的文本")


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
async def process_transcript(req: TranscriptRequest):
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

    dialogue_id = f"dialogue_{len(dialogues) + 1}"
    now = datetime.now().isoformat()

    dialogue = {
        'id': dialogue_id,
        'question': req.text.strip(),
        'answer': '等待大模型接入...',
        'is_valid': True,
        'rule': validation['rule'],
        'created_at': now
    }

    dialogues.append(dialogue)

    logger.info(f"有效问题已添加: {dialogue_id}")

    return {
        'code': 0,
        'message': 'success',
        'data': dialogue
    }


@router.get("/dialogues", response_model=TranscriptResponse)
async def get_dialogues():
    """获取当前会话的所有对话记录"""
    return {
        'code': 0,
        'message': 'success',
        'data': {
            'dialogues': dialogues
        }
    }


@router.delete("/dialogues", response_model=TranscriptResponse)
async def clear_dialogues():
    """清空所有对话记录"""
    global dialogues
    dialogues = []
    logger.info("对话记录已清空")
    return {
        'code': 0,
        'message': 'success'
    }