from datetime import datetime

from extensions import db


class SecurityEvent(db.Model):
    """n8n 이 판정한 허용/거부 결과를 저장하는 표.
    student 를 남겨 두면 제출 증적에 본인 식별자가 찍혀 채점·표절 확인이 쉽다."""
    __tablename__ = 'security_events'
    id = db.Column(db.Integer, primary_key=True)
    student = db.Column(db.String(50), nullable=False, index=True)  # 본인 식별자(필수)
    src_ip = db.Column(db.String(45), nullable=False, index=True)  # IPv6 까지 45자
    level = db.Column(db.Integer, nullable=False, default=0)
    rule = db.Column(db.String(50))
    fail_count = db.Column(db.Integer, nullable=False, default=0)
    decision = db.Column(db.String(10), nullable=False)  # allow | deny
    severity = db.Column(db.String(10), nullable=False, default='Low')
    reason = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)  # DB 저장 시각

    def to_dict(self):
        return {
            'id': self.id,
            'student': self.student,
            'src_ip': self.src_ip,
            'level': self.level,
            'rule': self.rule,
            'fail_count': self.fail_count,
            'decision': self.decision,
            'severity': self.severity,
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
