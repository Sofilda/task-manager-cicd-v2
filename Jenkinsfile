/*
 * Jenkinsfile — лабораторная работа №4, вариант 2.
 * Основа: базовый конвейер из методического пособия (часть 1).
 *
 * Индивидуальное задание, часть 1 (Jenkins, вариант 2):
 *   добавить параметр выбора ветки или режима проверки Pipeline.
 *   Реализованы оба параметра:
 *     BRANCH     — ветка Git, код которой проверяется (по умолчанию main);
 *     CHECK_MODE — режим проверки:
 *        COMPILE — только компиляция основного и тестового кода (самый быстрый);
 *        UNIT    — компиляция + модульные тесты (Surefire);
 *        FULL    — полный цикл: модульные + интеграционные тесты, JaCoCo, JAR.
 */

// Запуск команды оболочки: bat на Windows-агенте, sh на Linux-агенте.
def runCmd(String command) {
    if (isUnix()) {
        sh command
    } else {
        bat command
    }
}

pipeline {
    /*
     * На учебном стенде из методички: agent { label 'windows-java21-agent' }.
     * Здесь — любой узел с Git (Windows или Linux); JDK и Maven подключает блок tools.
     */
    agent any

    // Инструменты из Manage Jenkins → Tools (как в ЛР №3):
    // JDK с именем 'jdk21' и Maven с именем 'maven3'.
    tools {
        jdk 'jdk21'
        maven 'maven3'
    }

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
        // Код получаем сами на этапе Checkout — из выбранной ветки.
        skipDefaultCheckout()
    }

    environment {
        // Jenkinsfile всегда читается из main (Script Path),
        // а исходный код берётся из ветки, выбранной в параметре BRANCH.
        REPO_URL = 'https://github.com/Sofilda/task-manager-cicd-v2.git'
    }

    parameters {
        string(name: 'BRANCH', defaultValue: 'main', trim: true,
               description: 'Вариант 2: ветка Git для проверки (например, main или feature/extra-test)')
        choice(name: 'CHECK_MODE', choices: ['FULL', 'UNIT', 'COMPILE'],
               description: 'Вариант 2: режим проверки. FULL — все тесты + JaCoCo + JAR; ' +
                            'UNIT — только модульные тесты; COMPILE — только компиляция')
    }

    stages {
        stage('Validate Parameters') {
            steps {
                script {
                    // При самом первом запуске задания параметров ещё нет — берём значения по умолчанию.
                    env.SELECTED_BRANCH = (params.BRANCH ?: 'main').trim()
                    env.SELECTED_MODE   = params.CHECK_MODE ?: 'FULL'
                    // Имя ветки попадает в команду git, поэтому допускаем только безопасные символы.
                    if (!(env.SELECTED_BRANCH ==~ /[A-Za-z0-9._\/-]+/)) {
                        error("Недопустимое имя ветки: '${env.SELECTED_BRANCH}'. " +
                              'Разрешены латинские буквы, цифры и символы . _ / -')
                    }
                    currentBuild.description = "ветка ${env.SELECTED_BRANCH}, режим ${env.SELECTED_MODE}"
                    echo "Ветка: ${env.SELECTED_BRANCH}; режим проверки: ${env.SELECTED_MODE}"
                }
            }
        }

        stage('Checkout') {
            steps {
                echo "Получение кода из ветки ${env.SELECTED_BRANCH}"
                git url: env.REPO_URL, branch: env.SELECTED_BRANCH
                script {
                    env.CHECKED_OUT_COMMIT = isUnix() ?
                        sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim() :
                        bat(script: '@git rev-parse --short HEAD', returnStdout: true).trim()
                    echo "Проверяется commit ${env.CHECKED_OUT_COMMIT} из ветки ${env.SELECTED_BRANCH}"
                    currentBuild.description = "ветка ${env.SELECTED_BRANCH} (${env.CHECKED_OUT_COMMIT}), режим ${env.SELECTED_MODE}"
                }
            }
        }

        stage('Toolchain') {
            steps {
                runCmd 'java -version'
                runCmd 'mvn -version'
                runCmd 'git --version'
            }
        }

        // Выполняется во всех режимах: компиляция основного и тестового кода.
        stage('Compile') {
            steps {
                runCmd 'mvn -B -ntp clean test-compile'
            }
        }

        // UNIT и FULL: модульные тесты (Surefire) под агентом JaCoCo.
        stage('Unit Tests') {
            when { expression { env.SELECTED_MODE == 'UNIT' || env.SELECTED_MODE == 'FULL' } }
            steps {
                runCmd 'mvn -B -ntp test'
            }
        }

        // Только FULL: интеграционные тесты (Failsafe), отчёт JaCoCo и JAR.
        // -DskipUnitTests=true — модульные тесты уже выполнены на предыдущем этапе
        // и повторно не запускаются; покрытие дописывается в тот же jacoco.exec.
        stage('Integration Tests and Package') {
            when { expression { env.SELECTED_MODE == 'FULL' } }
            steps {
                runCmd 'mvn -B -ntp verify -DskipUnitTests=true'
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: 'target/surefire-reports/TEST-*.xml,target/failsafe-reports/TEST-*.xml'
            archiveArtifacts artifacts: 'target/surefire-reports/**,target/failsafe-reports/**,target/site/jacoco/**',
                             allowEmptyArchive: true
        }
        success {
            script {
                if (env.SELECTED_MODE == 'FULL') {
                    archiveArtifacts artifacts: 'target/task-manager-cicd-1.0.0.jar', fingerprint: true
                }
            }
            echo "Проверка ветки ${env.SELECTED_BRANCH} в режиме ${env.SELECTED_MODE} завершена успешно"
        }
        failure {
            echo "Проверка ветки ${env.SELECTED_BRANCH} в режиме ${env.SELECTED_MODE} завершилась ошибкой — см. журнал этапа"
        }
    }
}
