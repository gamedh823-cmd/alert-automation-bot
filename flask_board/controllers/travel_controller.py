"""부산 여행정보 (공공데이터 Open API)."""
import re

import requests
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from extensions import db
from models import Post

travel_bp = Blueprint('travel', __name__, url_prefix='/api/travel')

_travel_cache = None


def get_travel_cache():
    """전체 데이터를 한 번만 받아와서 메모리에 캐싱 (외부 API 반복 호출 방지)"""
    global _travel_cache
    if _travel_cache is None:
        url = (
            f"{current_app.config['PUBLIC_API_URL']}"
            f"?serviceKey={current_app.config['PUBLIC_API_KEY']}"
            f"&pageNo=1&numOfRows=500&resultType=json"
        )
        res = requests.get(url)
        data = res.json()
        items = data.get('getRecommendedKr', {}).get('item', [])

        results = []
        for it in items:
            title = it.get("MAIN_TITLE") or ""
            title = re.sub(r'\s*\([^)]*\)\s*$', '', title)  # 끝에 붙은 (한,영,중간,중번,일) 같은 표기 제거
            results.append({
                "seq": it.get("UC_SEQ"),
                "title": title,
                "subtitle": it.get("SUBTITLE"),
                "gugun": it.get("GUGUN_NM"),
                "category": it.get("CATE2_NM"),
                "addr": it.get("ADDR1"),
                "tel": it.get("CNTCT_TEL"),
                "homepage": it.get("HOMEPAGE_URL"),
                "traffic": it.get("TRFC_INFO"),
                "content": it.get("ITEMCNTNTS"),
                "img_thumb": it.get("MAIN_IMG_THUMB"),
                "img_normal": it.get("MAIN_IMG_NORMAL"),
            })
        _travel_cache = results
    return _travel_cache


@travel_bp.route('', methods=['GET'])
def get_travel():
    page_no = request.args.get('pageNo', default=1, type=int)
    num_of_rows = request.args.get('numOfRows', default=12, type=int)

    all_items = get_travel_cache()
    total = len(all_items)
    total_pages = (total + num_of_rows - 1) // num_of_rows

    start = (page_no - 1) * num_of_rows
    end = start + num_of_rows
    page_items = all_items[start:end]

    return jsonify({
        "items": page_items,
        "total": total,
        "totalPages": total_pages,
        "pageNo": page_no,
    })


@travel_bp.route('/save', methods=['POST'])
@jwt_required()
def save_travel_to_board():
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    seq = data.get('seq')

    all_items = get_travel_cache()
    item = next((i for i in all_items if i['seq'] == seq), None)
    if not item:
        return jsonify({"msg": "해당 여행정보를 찾을 수 없습니다."}), 404

    content_text = re.sub('<[^>]*>', '', item.get('content') or '')
    body = f"{item.get('addr') or ''}\n\n{content_text}".strip()

    new_post = Post(
        title=f"[부산여행] {item.get('title') or ''}",
        content=body,
        category='여행',
        author_id=current_user_id,
    )
    db.session.add(new_post)
    db.session.commit()
    return jsonify({"msg": "게시판에 등록되었습니다.", "post_id": new_post.id}), 201
