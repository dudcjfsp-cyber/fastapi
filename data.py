from database import get_db_connection
from services.user_service import get_all_members, get_member, get_ootd
from services.course_service import get_all_courses, register_student, get_enrollments, delete_enrollment
from services.appeal_service import create_appeal, get_appeals
from services.shop_service import get_items, get_user_gold, get_inventory, buy_item, sell_item, sell_all_items, play_gacha_fixed, play_gacha_dynamic

# Backward compatibility for scripts using data.py directly
# All functions are re-exported
