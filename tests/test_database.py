import pytest
import database


@pytest.fixture(autouse=True)
def use_temp_db(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "test.db")
    database.init_db()


def test_seed_data_populates_empty_db():
    result = database.seed_data()
    assert "Успешно добавлено" in result


def test_seed_data_skips_when_already_seeded():
    # First call seeds; second call must not raise and must report existing data.
    database.seed_data()
    result = database.seed_data()
    assert "наполнена" in result


def test_get_instruction_returns_none_for_missing():
    assert database.get_instruction("admin", "nonexistent") is None


def test_set_and_get_instruction_roundtrip():
    database.set_instruction_content("admin", "opening", text_content="Hello")
    row = database.get_instruction("admin", "opening")
    assert row is not None
    assert row["text_content"] == "Hello"


def test_set_instruction_upsert():
    database.set_instruction_content("admin", "opening", text_content="v1")
    database.set_instruction_content("admin", "opening", text_content="v2")
    row = database.get_instruction("admin", "opening")
    assert row["text_content"] == "v2"


def test_init_db_creates_instructions_table():
    # get_instruction and set_instruction_content rely on the instructions table;
    # verifying they work confirms init_db created it.
    database.set_instruction_content("master", "sterilization", text_content="steps")
    row = database.get_instruction("master", "sterilization")
    assert row["role"] == "master"
    assert row["key"] == "sterilization"
