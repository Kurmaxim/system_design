        deploymentEnvironment "Production" {
            deploymentNode "iOS Device" {
                    description "Мобильные телефоны и планшеты клиентов во внешней сети"
                    properties {
                        "os" "iOS"
                        "ram" "8"
                    }

                    containerInstance guard_system.client_mobile_app
            }

            deploymentNode "Android Device" {
                    description "Мобильные телефоны и планшеты клиентов во внешней сети"
                    containerInstance guard_system.client_mobile_app
                    properties {
                        "os" "Android"
                        "cpu" "2"
                        "ram" "8"
                        "hdd" "70"
                    }
            }

            deploymentNode "Client Device 2" {
                    description "Стационарные компьютеры пользователей во внешней сети или мобильные устройства с установленным браузером"
                    properties {
                        "os" "Windows/MacOS/Linux Ubuntu"
                        "cpu" "4"
                        "ram" "8"
                        "hdd" "70"
                    }
                    containerInstance guard_system.client_web_app
            }

            
            deploymentNode "DMZ" {

            
                deploymentNode "BFF Server Mobile" {
                        description "Backend для мобильного приложения"
                        instances 3

                         properties {
                                "os" "Oracle Enteprise Linux"
                                "cpu" "4"
                                "ram" "16"
                                "hdd" "70"
                        }
                        containerInstance guard_system.client_mobile_app_backend 
                }


                bffw1 = deploymentNode "BFF Server Web" {
                        description "Backend для веба"
                        instances 3
                         properties {
                                "os" "Oracle Enteprise Linux"
                                "cpu" "4"
                                "ram" "16"
                                "hdd" "70"
                        }
                        containerInstance guard_system.client_web_app_backend
                }
            }

            deploymentNode "BPM Cluster" {
                deploymentNode "BPM" {
                        !script groovy {             
                                element.description = workspace.model.softwareSystems.find{
                                        element -> element.name=='Мобильный телохранитель'}.containers.find { 
                                                element -> element.name=='BPM'}.description
                        }
                        instances 2
                        properties {
                                "os" "Oracle Enteprise Linux"
                                "cpu" "4"
                                "ram" "8"
                                "hdd" "70"
                        }
                       containerInstance guard_system.bpm
                }
            }
            
            deploymentNode "Inventory server" {
                !script groovy {             
                        element.description = workspace.model.softwareSystems.find{
                                 element -> element.name=='Мобильный телохранитель'}.containers.find { 
                                        element -> element.name=='Inventory'}.description
                }
                properties {
                        "os" "Oracle Enteprise Linux"
                        "cpu" "4"
                        "ram" "8"
                        "hdd" "70"
                }
                containerInstance guard_system.inventory          
            }


            deploymentNode "Tracker First" {
                        !script groovy {             
                                element.description = workspace.model.softwareSystems.find{
                                        element -> element.name=='Мобильный телохранитель'}.containers.find { 
                                                element -> element.name=='Tracker'}.description
                        }
                        properties {
                                "os" "Oracle Enteprise Linux"
                                "cpu" "4"
                                "ram" "8"
                                "hdd" "70"
                        }
                        containerInstance guard_system.tracker
            }



            deploymentNode "Billing" {
                !script groovy {             
                        element.description = workspace.model.softwareSystems.find{
                                 element -> element.name=='Мобильный телохранитель'}.containers.find { 
                                        element -> element.name=='Billing'}.description
                }
                
                properties {
                                "os" "Oracle Enteprise Linux"
                                "cpu" "4"
                                "ram" "32"
                                "hdd" "70"
                        }
                containerInstance guard_system.billing
            }

        }

