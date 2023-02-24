#!/usr/bin/groovy

def json_release_file = ''
def String[] pkg_list = []
def download_dir = ''
def pkgs_signed = ''
def pkgs_upload = ''
def build_job = ''

pipeline {
    environment {
        GPG_PRIVATE_KEY = credentials('6e2f2e3c-9368-4aae-b017-a5bae4591ce4')
        GPG_PRIVATE_KEY_PASSPHRASE = credentials('d8ec011f-236a-404e-a6cb-ac6f9adfae82')
        GPG_PUBLIC_KEY = credentials('eef6cd3d-b410-489d-86fb-349a53abe498')
        NEXUS_CONFIG = credentials('ecfb20e4-0c97-48e3-9e36-50e42b0e59f1')
    }

    agent {
        dockerfile {
            filename 'Dockerfile.build'
        }
    }
    stages {
        stage('Install dependencies') {
            steps {
                withPythonEnv('python3') {
                   sh 'pip3 install --user -r requirements.txt'
                }
            }
        }
        stage('Detect release changes') {
            when {
                changeRequest()
            }
            steps {
                script {
                    last_commit = sh(
                        returnStdout: true,
                        script: 'git diff-tree --name-only --no-commit-id -r HEAD').trim()
                    json_files_changed = []
                    last_commit.split('\n').each {
                        if (it.contains('.json')) {
                            json_files_changed.add(it)
                        }
                    }
                    if (json_files_changed.size() == 0) {
                        println('No changes detected to any JSON release file')
                    }
                    else if (json_files_changed.size() > 1) {
                        currentBuild.result = 'ABORTED'
                        error('More than one modified JSON release file found. Please commit one JSON at a time')
                    }
                    else {
                        println("Changes to ${json_files_changed[0]} found. Processing file..")
                        json_release_file = json_files_changed[0]
                    }
                }
            }
        }

        stage('Collect the list of packages') {
            when {
                expression {return json_release_file}
            }
            steps {
                dir('scripts') {
                    withPythonEnv('python3') {
                        script {
                            pkg_list = sh(
                                returnStdout: true,
                                script: "python3 json_parser.py ${json_release_file} 0"
                            ).trim()
                        }
                    }
                }
            }
        }

        stage('Download the packages to a temporary directory') {
            when {
                expression {return pkg_list}
            }
            steps {
                dir('scripts') {
                    withPythonEnv('python3') {
                        script {
                            download_dir = sh(
                                returnStdout: true,
                                script: "python3 download_pkgs.py ${json_release_file} 0"
                            ).trim()
                            println(download_dir)
                        }
                    }
                }
            }
        }

        stage('Add UMD GPG key'){
            when {
                expression {return download_dir}
            }
            steps {
                println('Importing private GPG key')
                sh "gpg --import --batch --yes $GPG_PRIVATE_KEY"
                sh 'gpg --list-keys'
                println('Importing public GPG key for RPM')
                sh "rpm -q gpg-pubkey --qf '%{name}-%{version}-%{release} --> %{summary}\n'"
                sh "sed -i \"s/--passphrase ''/--passphrase '$GPG_PRIVATE_KEY_PASSPHRASE'/g\" ~/.rpmmacros"
                dir('scripts') {
                    script {
                        pkgs_signed = sh(
                            returnStdout: true,
                            script: "./rpm_sign.sh ${download_dir} 0"
                        ).trim()
                    	println(pkgs_signed)
                        sh "./rpm_sign.sh ${download_dir} 1"
                    }
                }
            }
        }

        stage('Upload packages'){
            when {
                expression {return download_dir}
            }
            steps {
                dir('scripts') {
                    script {
                        pkgs_upload = sh(
                            returnStdout: true,
                            script: "python3 upload_pkgs.py ${json_release_file} 0" + ' ${NEXUS_CONFIG}'
                        ).trim()
                        println(pkgs_upload)
                    }
                } 
            }
        }

        // stage('Trigger validation'){
        //     when {
        //         expression {return pkgs_upload}
        //     }
        //     steps {
        //         script {
        //             build_job = build job: 'QualityCriteriaValidation/package-install',
        //                         parameters: [ // these values need to be extracted from the JSON
        //                             string(name: 'Release', value: 'UMD4'),
        //                             text(name: 'OS', value: 'centos7'),
        //                             text(name: 'Verification_repository', value: 'https://nexusrepoegi.a.incd.pt/repository/umd/'),
        //                             text(name: 'Packages', value: 'condor'),
        //                             booleanParam(name: 'enable_testing_repo', value: false),
        //                             booleanParam(name: 'enable_untested_repo', value: false),
        //                             booleanParam(name: 'disable_updates_repo', value: false)
        //                         ]
        //         }
        //     }
        // }

        stage('Check build job status') {
            // when {
            //     branch 'master' 
            // }
            steps {
                dir('scripts') {
                    println('########')
                    println(json_release_file)
                    println('########')
                    script {
                        pkgs_cleanup = sh(
                            returnStdout: true,
                            script: "python3 cleanup.py ${json_release_file}" + ' ${NEXUS_CONFIG}'
                        ).trim()
                    }
                }
            }
        }
    }
}
