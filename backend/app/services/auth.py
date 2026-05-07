"""认证业务逻辑"""
import bcrypt
from datetime import datetime, timedelta
from ..database import get_db
from ..config import PIN_MAX_ATTEMPTS, PIN_LOCK_MINUTES


def handle_login(student_id: str) -> dict:
    with get_db() as db:
        row = db.execute("SELECT id, name, pin, in_roster FROM users WHERE student_id=?", (student_id,)).fetchone()
        if not row:
            name = student_id[-4:] + "同学"
            cur = db.execute("INSERT INTO users (student_id, name, in_roster) VALUES (?,?,0)", (student_id, name))
            user_id = cur.lastrowid
            return {"status": "need_setup", "name": name, "need_pin": False, "user_id": user_id}
        if not row["pin"]:
            return {"status": "need_setup", "name": row["name"], "need_pin": False, "user_id": row["id"]}
        return {"status": "need_pin", "name": row["name"], "need_pin": True, "user_id": row["id"]}


def verify_pin(student_id: str, pin: str) -> dict:
    with get_db() as db:
        row = db.execute("SELECT id, pin, pin_attempts, pin_locked_until, name FROM users WHERE student_id=?", (student_id,)).fetchone()
        if not row or not row["pin"]:
            raise ValueError("用户不存在或未设置 PIN")

        if row["pin_locked_until"] and datetime.fromisoformat(row["pin_locked_until"]) > datetime.now():
            raise ValueError("账户已锁定，请稍后再试")

        if not bcrypt.checkpw(pin.encode(), row["pin"].encode()):
            attempts = row["pin_attempts"] + 1
            if attempts >= PIN_MAX_ATTEMPTS:
                locked = (datetime.now() + timedelta(minutes=PIN_LOCK_MINUTES)).isoformat()
                db.execute("UPDATE users SET pin_attempts=?, pin_locked_until=? WHERE id=?", (attempts, locked, row["id"]))
            else:
                db.execute("UPDATE users SET pin_attempts=? WHERE id=?", (attempts, row["id"]))
            db.commit()
            raise ValueError(f"PIN 错误，剩余尝试 {PIN_MAX_ATTEMPTS - attempts} 次")

        db.execute("UPDATE users SET pin_attempts=0, pin_locked_until=NULL WHERE id=?", (row["id"],))
        return {"user_id": row["id"], "name": row["name"]}


def set_pin(user_id: int, pin: str, old_pin: str | None = None) -> None:
    with get_db() as db:
        row = db.execute("SELECT pin, name FROM users WHERE id=?", (user_id,)).fetchone()
        if row and row["pin"] and old_pin is None:
            raise ValueError("修改 PIN 需要提供旧 PIN")
        if row and row["pin"]:
            if not bcrypt.checkpw(old_pin.encode(), row["pin"].encode()):
                raise ValueError("旧 PIN 错误")
        hashed = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
        db.execute("UPDATE users SET pin=? WHERE id=?", (hashed, user_id))


def get_me(user_id: int) -> dict:
    with get_db() as db:
        row = db.execute("SELECT student_id, name, prog_mode, sound_on, vibrate_on FROM users WHERE id=?", (user_id,)).fetchone()
        return dict(row)


def update_settings(user_id: int, data: dict) -> None:
    with get_db() as db:
        for field in ("prog_mode", "sound_on", "vibrate_on"):
            if field in data and data[field] is not None:
                db.execute(f"UPDATE users SET {field}=? WHERE id=?", (data[field], user_id))


def reset_pin(student_id: str) -> None:
    with get_db() as db:
        db.execute("UPDATE users SET pin=NULL, pin_attempts=0, pin_locked_until=NULL WHERE student_id=?", (student_id,))
