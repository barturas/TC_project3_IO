# test_question_manager.py
import pytest
from main import QuestionManager, QuizQuestions, FreeFormQuestions

def test_add_question():
    qm = QuestionManager()
    original_len = len(qm.questions)
    qm.questions.append(QuizQuestions(1, "Test question", ["A", "B", "C"], "A"))
    assert len(qm.questions) == original_len + 1, "Failed to add a quiz question"

def test_delete_question():
    qm = QuestionManager()
    qm.questions.append(QuizQuestions(1, "Test question", ["A", "B", "C"], "A"))
    original_len = len(qm.questions)
    qm.delete_question(1)
    assert len(qm.questions) == original_len - 1, "Failed to delete a question"

def test_toggle_question_active():
    qm = QuestionManager()
    qm.questions.append(QuizQuestions(1, "Test question", ["A", "B", "C"], "A"))
    original_status = qm.questions[0].is_active
    qm.toggle_question_active(1)
    assert qm.questions[0].is_active != original_status, "Failed to toggle active status"
