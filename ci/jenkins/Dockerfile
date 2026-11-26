# Jenkins LTS с JDK 21, Maven и плагинами, нужными Jenkinsfile.
FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update && apt-get install -y --no-install-recommends maven && rm -rf /var/lib/apt/lists/*
USER jenkins

RUN jenkins-plugin-cli --plugins \
    workflow-aggregator git junit timestamper pipeline-stage-view \
    configuration-as-code mailer

COPY casc.yaml /usr/share/jenkins/ref/casc.yaml
COPY job-config.xml /usr/share/jenkins/ref/jobs/Task-Manager-Variant2/config.xml

ENV CASC_JENKINS_CONFIG=/usr/share/jenkins/ref/casc.yaml
# Учебный стенд на одноразовой машине: без мастера установки и CSRF.
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false \
 -Dhudson.security.csrf.GlobalCrumbIssuerConfiguration.DISABLE_CSRF_PROTECTION=true \
 -Dfile.encoding=UTF-8 -Duser.timezone=Europe/Minsk"
