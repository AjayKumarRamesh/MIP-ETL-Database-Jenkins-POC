# Installing Liquibase on Linux

## Prerequisite
    1. Make sure java installed ($ apt install openjdk-11-jdk -y)
	2. Ensure that the Liquibase executable location is in the PATH environment variable.
	3. Download the Liquibase DB2 extension for iSeries support.
	4. Ensure that you have installed the correct JDBC driver jar file.

## Step 1. Download the liquibase
	$ mkdir /opt/liquibase && cd /opt/liquibase
	$ wget https://github.com/liquibase/liquibase/releases/download/v4.8.0/liquibase-4.8.0.tar.gz
	$ tar -zxvf liquibase-4.8.0.tar.gz

## Step 2. Add the Liquibase installation directory to your system PATH.
	$ echo "export PATH=${PATH}:/opt/liquibase" >> /etc/profile
	$ source /etc/profile

## Step 3. Verify the Liquibase whether istalled or not.
    From a command line or terminal, type below command to verify that Liquibase has been installed successfully

    $ liquibase --help

## Step 4. Install Liqibase DB2 extension
	$ cd /opt/liquibase/lib/
	$ wget https://github.com/liquibase/liquibase-db2i/releases/download/liquibase-db2i-4.8.0/liquibase-db2i-4.8.0.jar

## Step 5. Download JDBC Driver (https://www.ibm.com/support/pages/db2-jdbc-driver-versions-and-downloads)



# Create the Liquibase Project

To create a Liquibase project with DB2 LUW, perform the following steps:

	1. Create a new project folder and name it LiquibaseDB2LUW.

	2. In your LiquibaseDB2LUW folder, create a new text file and name it liquibase.properties.

	3. Edit the liquibase.properties file to add the following properties:
		changeLogFile: dbchangelog.sql
		url: jdbc:db2://192.168.1.15:5432/MYDATABASE:sslConnection=true;
		username: user
		password: password
		driver: com.ibm.db2.jcc.DB2Driver

	4. Verify the project configuration. Run the status command to verify that the configuration is complete. Open a command prompt and navigate to the project folder LiquibaseDB2LUW. Run the command as follows:
		$ liquibase status

	5. Verify that the DATABASECHANGELOG and DATABASECHANGELOGLOCK tables were created. From a database UI Tool, check your new Liquibase tables.
