pipeline {
    agent any

    stages {
        
        stage("Install Liquibase") {
            environment {
                LIQUIBASE_HOME = "${HOME}/liquibase"
                
                //Add Liquibase Home to the PATH Env variable.
                PATH = "${PATH}:${LIQUIBASE_HOME}"
                
            }

            steps {
                //Display installed Java version
                sh('java -version')
                
                // Assign Liquibase version
                def LIQUIBASE_VERSION = "4.8.0"
                sh('echo ${LIQUIBASE_VERSION}')
                // sh('echo ${env.LIQUIBASE_VERSION}')
                // sh('${env.LIQUIBASE_VERSION}')
                
                //Installs Liquibase and adds it to the PATH
                sh('mkdir ${LIQUIBASE_HOME} && cd ${LIQUIBASE_HOME} && wget -qO- https://github.com/liquibase/liquibase/releases/download/v${LIQUIBASE_VERSION}/liquibase-${LIQUIBASE_VERSION}.tar.gz | tar xvz')


                //Install DB2 JDBC driver from Maven repo to lib/ folder
                sh('cd ${LIQUIBASE_HOME}/lib && wget -q https://repo1.maven.org/maven2/com/ibm/db2/jcc/11.5.7.0/jcc-11.5.7.0.jar')
                
                //runs liquibase
                sh ("echo ${PATH}")
                sh('liquibase --version')
                // sh('liquibase --changeLogFile=dbchangelog.xml update')
            }
        } //stage
        stage("Deploy the DB2 changes") {
            steps {
                sh('echo ${GIT_COMMIT}')
                sh('echo ${WORKSPACE}')
                sh('git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only')
            }
        }
        
    } //stages
} //pipeline
