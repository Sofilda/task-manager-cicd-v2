package by.edu.example.taskmanager.service;

import by.edu.example.taskmanager.exception.TaskNotFoundException;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Дополнительный модульный тест ветки feature/extra-test (вариант 2).
 * Нужен, чтобы по числу тестов было видно, что Jenkins проверил именно выбранную ветку.
 */
class TaskServiceExtraTest {

    @Test
    void deleteUnknownTaskThrowsNotFound() {
        TaskService service = new TaskService();
        assertThrows(TaskNotFoundException.class, () -> service.delete(12345L));
    }
}
