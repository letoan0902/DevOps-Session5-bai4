"""Dich vu nguoi dung - phien ban 1.0.1 (hotfix: khong lo du lieu nhay cam)."""

USERS = {
    1: {
        "id": 1,
        "username": "lan.nguyen",
        "email": "lan.nguyen@example.com",
        "password_hash": "pbkdf2:sha256:600000:s4lt1:9f2c7a1be44d03c5a8e1f6b2d7c9a0e3",
        "role": "admin",
    },
    2: {
        "id": 2,
        "username": "minh.tran",
        "email": "minh.tran@example.com",
        "password_hash": "pbkdf2:sha256:600000:s4lt2:1b8e5d3f0a62c9e7d4b1a8f3c5e20d96",
        "role": "member",
    },
}


def mask_email(email):
    """Che bot email: giu 2 ky tu dau cua phan local, an phan con lai."""
    local, _, domain = email.partition("@")
    return local[:2] + "***@" + domain


def get_user_profile(user_id):
    """Tra ve ho so cong khai cua nguoi dung (whitelist cac truong an toan)."""
    user = USERS.get(user_id)
    if user is None:
        return None
    # Chi tra ve cac truong duoc phep. TUYET DOI khong tra ve password_hash.
    return {
        "id": user["id"],
        "username": user["username"],
        "email": mask_email(user["email"]),
        "role": user["role"],
    }
