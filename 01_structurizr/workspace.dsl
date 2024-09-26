workspace {
    name "Мобильный телохранитель"
    description "демонстрационный пример для показа техник ведения проектной документацииы"
    !adrs decisions
    !docs documentation
    !identifiers hierarchical

    model {
        !include model.dsl 
        !include deployment_model.dsl  
    }

    views {
        themes default

        systemLandscape "SystemLandscape"{
            include *
            autoLayout lr
        }

        systemContext guard_system "Context" {
            include *
            autoLayout
        }

        container guard_system "Containers" {
            include *
            autoLayout
        }
        
        component guard_system.billing "Billing"{
            include *
            autoLayout lr
            animation {
                guard_system.bpm
                guard_system.tracker
                guard_system.billing.billing_queue
                guard_system.billing.billing_controller
                guard_system.billing.billing_database  
                payment_system
                guard_system.billing.billing_facade
            }
        }

        component guard_system.inventory "Inventory"{
            include *
            autoLayout lr
        }

        component guard_system.crm "CRM"{
            include *
            autoLayout
        }

        component guard_system.tracker "Tracking"{
            include *
            autoLayout
        }

        deployment guard_system "Production" "vs"{
            include *
            description "Типовое размещение оборудования"

            autoLayout
        }

        dynamic guard_system "UC01" {
            autoLayout lr
            description "Тестовый сценарий"

            user -> guard_system.client_mobile_app "1. Клиент открывает мобильное приложение"
            guard_system.client_mobile_app -> sso.authorization_password "2. Мобильное приложение запрашивает данные для аутентификации клиента (login/password) и проверяет их через WebSSO"
            user -> guard_system.client_mobile_app "3. Клиент выбирает раздел Заказ дрона"
            guard_system.client_mobile_app -> guard_system.client_mobile_app_backend "4. Мобильное приложение запрашивает backend для поиска дрона"
            guard_system.client_mobile_app_backend -> guard_system.bpm "5. Backend мобильного приложения запускает на BPM сценарий поиска дрона"
            guard_system.bpm -> guard_system.crm "6. BPM получает в CRM данные по клиенту и его детям"
            guard_system.bpm -> guard_system.crm "7. BPM получает информацию о маршруте ребенка"
            guard_system.bpm -> mlc "8. BPM получает информацию о текущем положении ребенка из MLC"
            guard_system.bpm -> guard_system.billing  "9. BPM получает данные по достаточности баланса у клиента"
            guard_system.bpm -> guard_system.inventory "10. BPM получает данные в inventory о свободных дронах"
            guard_system.bpm -> guard_system.tracker "11. BPM передает команду на дрона о начале трэкинга" 
            
        }
        
        styles {
            element "Person" {
                color #ffffff
                fontSize 22
                shape Person
            }
            element "Customer" {
                background #08427b
            }

            element "ExternalSystem" {
                background #c0c0c0
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "WebBrowser" {
                shape WebBrowser
            }
            element "MobileApp" {
                shape MobileDevicePortrait
            }
            element "Database" {
                shape Cylinder
            }
            element "Queue" {
                shape Pipe
            }
            element "Component" {
                background #85bbf0
                color #000000
                shape Component
            }

            
        }
    }

}