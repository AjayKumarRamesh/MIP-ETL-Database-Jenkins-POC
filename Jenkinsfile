// Assign Liquibase version
// def LIQUIBASE_VERSION = "4.8.0"

pipeline {
    agent any

    stages {
        
        stage("Install Liquibase") {
            environment {
                //Add Liquibase Home to the PATH Env variable.
                LIQUIBASE_HOME = "${HOME}/liquibase"
                LIQUIBASE_VERSION = "4.8.0"                
                PATH = "${PATH}:${LIQUIBASE_HOME}"
            }
            steps {

                // script {
                //     LIQUIBASE_VERSION = "4.8.0"
                // }

                // // Assign Liquibase version
                // LIQUIBASE_VERSION = "4.8.0"

                //Display installed Java version
                sh('java -version')
                
                
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
            environment {
                //Add Liquibase Home to the PATH Env variable.
                LIQUIBASE_HOME = "${HOME}/liquibase"          
                PATH = "${PATH}:${LIQUIBASE_HOME}"
            }
            steps {
                sh('echo ${GIT_COMMIT}')
                sh('echo ${WORKSPACE}')
                // script {
                //     git_changes = sh ( script: 'git diff ${GIT_PREVIOUS_SUCCESSFUL_COMMIT}..${GIT_COMMIT} --name-only', returnStdout: true)
                //     }
                sh ('bash deploy_db_changes.sh ${GIT_PREVIOUS_SUCCESSFUL_COMMIT} ${GIT_COMMIT}')
                    
                
            }
        }
        
    } //stages
} //pipeline
