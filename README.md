# task-manager-cicd-v2 — ЛР №4 (ИППРПО), вариант 2

Веремчук Валентин Сергеевич, группа 472302.

Учебное REST-приложение (Spring Boot, байт-код Java 17) и два CI-конвейера:

* `Jenkinsfile` — Jenkins Declarative Pipeline. Вариант 2, часть 1: параметры выбора ветки
  (`BRANCH`) и режима проверки (`CHECK_MODE`: FULL / UNIT / COMPILE).
* `.github/workflows/ci.yml` — GitHub Actions. Вариант 2, часть 2: Matrix-проверка на JDK 17 и JDK 21.
* `.github/workflows/jenkins-demo.yml` — учебный стенд: Jenkins LTS в Docker на runner-е,
  прогон контрольных сценариев, журналы и скриншоты — в ветке `ci-evidence`.
* Ветка `feature/extra-test` — демонстрационная ветка с дополнительным модульным тестом.

Локальная проверка:

    mvn -B -ntp clean verify
