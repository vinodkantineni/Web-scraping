from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import User, Analysis
from ..schemas import AnalysisRequest, AnalysisResponse
from ..auth import get_current_user
from ..ml.analyzer import analyze_article

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

@router.post("/analyze", response_model=AnalysisResponse)
def analyze(payload: AnalysisRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    try:
        # Perform extraction & analysis (Gemini or BART)
        analysis_data = analyze_article(url=payload.url, raw_text=payload.text)
        
        # Save to database
        db_analysis = Analysis(
            user_id=current_user.id,
            title=analysis_data["title"],
            url=payload.url,
            text=analysis_data["text"],
            summary=analysis_data["summary"],
            original_left=analysis_data["original_left"],
            original_center=analysis_data["original_center"],
            original_right=analysis_data["original_right"],
            debiased_text=analysis_data["debiased_text"],
            debiased_left=analysis_data["debiased_left"],
            debiased_center=analysis_data["debiased_center"],
            debiased_right=analysis_data["debiased_right"],
            bias_reduction=analysis_data["bias_reduction"]
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
        
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/history", response_model=List[AnalysisResponse])
def get_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Query all analyses for the current logged-in user, ordered by date descending
    history = db.query(Analysis).filter(Analysis.user_id == current_user.id).order_by(Analysis.created_at.desc()).all()
    return history


@router.delete("/history/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(analysis_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Check if analysis exists and belongs to the current user
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id, Analysis.user_id == current_user.id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="History item not found or you don't have permission to delete it"
        )
    
    db.delete(analysis)
    db.commit()
    return
