workspace {
    name "Планирование задач"
    description "Система для управления целями, задачами и пользователями."

    !identifiers hierarchical

    model {

        u1 = person "Пользователь" "Пользователь системы, который создает задачи и цели."
        u2 = person "Администратор" "Администратор системы, управляющий пользователями."

        s1 = softwareSystem "Планирование задач" {

            db = container "Database" {
                technology "PostgreSQL 14"
                description "Хранилище данных для пользователей, целей и задач."
            }

            userService = container "User Service" {
                technology "Python FastAPI"
                description "Сервис для управления пользователями."
                -> db "Сохранение и получение информации о пользователях" "SQL"
            }

            taskService = container "Task Service" {
                technology "Python FastAPI"
                description "Сервис для управления целями и задачами."
                -> db "Сохранение и получение информации о целях и задачах" "SQL"
            }

            apiGateway = container "API Gateway" {
                technology "Node.js с Express"
                description "Центральный узел для обработки всех API запросов."
                -> userService "Управление пользователями" "HTTPS"
                -> taskService "Управление целями и задачами" "HTTPS"
            }

            fe = container "Single Page Application" {
                technology "JS, React"
                description "Веб-интерфейс для взаимодействия с системой."
                -> apiGateway "Получение/изменение данных" "HTTPS"
            }
        }

        u1 -> s1.fe "Создать цель, задачу, изменить статус задачи"
        u2 -> s1.fe "Создать пользователя, найти пользователя"

        deploymentEnvironment "Production" {

            deploymentNode "DMZ" {
                deploymentNode "NGinx Server" {
                    containerInstance s1.fe
                    instances 2
                }
            }

            deploymentNode "Inside" {

                in_db = infrastructureNode "Backup Database Server"
                dn_db = deploymentNode "Database Server" {
                    containerInstance s1.db
                    -> in_db "Backup"
                }

                deploymentNode "k8s pod backend" {
                    containerInstance s1.apiGateway
                    instances 3
                }

                deploymentNode "k8s pod userService" {
                    containerInstance s1.userService
                }

                deploymentNode "k8s pod taskService" {
                    containerInstance s1.taskService
                }

            }

        }

    }

    views {

        dynamic s1 "uc01" "Создание новой задачи" {
            autoLayout lr

            u1 -> s1.fe "Открыть страницу задач"
            s1.fe -> s1.apiGateway "POST /tasks"
            s1.apiGateway -> s1.taskService "POST /tasks"
            s1.taskService -> s1.db "INSERT INTO tasks (...) VALUES (...)"
        }

        dynamic s1 "uc02" "Поиск пользователя по логину" {
            autoLayout lr

            u2 -> s1.fe "Ввести логин пользователя"
            s1.fe -> s1.apiGateway "GET /users?login={login}"
            s1.apiGateway -> s1.userService "GET /users?login={login}"
            s1.userService -> s1.db "SELECT * FROM users WHERE login={login}"
        }

        themes default
        systemContext s1 {
            include *
            autoLayout
        }

        container s1 "vertical" {
            include *
            autoLayout
        }

        container s1 "horizontal" {
            include *
            autoLayout lr
        }

        component s1.apiGateway {
            include *
            autoLayout lr
        }

        deployment * "Production" {
            include *
            autoLayout
        }

    }
}