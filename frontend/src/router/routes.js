import store from '@/state/store'

export default [
    {
        path: '/',
        name: 'home',
        meta: {
            authRequired: true,
        },
        beforeEnter: (to, from, next) => {
            if (store.getters['auth/loggedIn']) {
                return store.dispatch('auth/validate').then((res) => {
                    let data = res.data
                    data.errcode == 0 ? next() : next({name: "login"})
                })
            } else {
                // Continue to the login page
                next({name: 'login'})
            }
        },
        component: () => import('../views/pages/index'),
        children: [
            {
                path: "",
                redirect: "dataStatistics"
            },
            {
                path: "dataStatistics",
                component: () => import('../views/pages/content/data-statistics')
            },
            {
                path: "filesManagement",
                component: () => import('../views/pages/content/files-management')
            },
            {
                path: "personalMessage",
                component: () => import('../views/pages/content/personal-message')
            },
            {
                path: "messageManagement",
                component: () => import('../views/pages/content/message-management')
            },
            {
                path: "myBorrowRecord",
                component: () => import('../views/pages/content/my-borrow-record')
            },
            {
                path: "borrowRecordManagement",
                component: () => import('../views/pages/content/borrow-record-management')
            },
            {
                path: "filingAudit",
                component: () => import('../views/pages/content/filing-audit')
            },
            {
                path: "fileAudit",
                component: () => import('../views/pages/content/file-audit')
            },
            {
                path: "basicSetting",
                component: () => import('../views/pages/content/basic-setting')
            },
            {
                path: "securitySetting",
                component: () => import('../views/pages/content/security-setting')
            },
            {
                path: "userManagement",
                component: () => import('../views/pages/content/user-management')
            },
            {
                path: "roleManagement",
                component: () => import('../views/pages/content/role-management')
            }
        ]
    },
    {
        path: '/login',
        name: 'login',
        component: () => import('../views/pages/account/login'),
        beforeEnter: (to, from, next) => {
            if (store.getters['auth/loggedIn']) {
                return store.dispatch('auth/validate').then((res) => {
                    let data = res.data
                    data.errcode == 0 ? next({ name: 'home' }) : next()
                })
            } else {
                // Continue to the login page
                next()
            }
        },
        meta: {

        },
    },
   
]
