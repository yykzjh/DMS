export const menuItems = [
    {
        id: 1,
        label: "menuitems.homepage.text",
        icon: 'ri-home-gear-fill',
        subItems: [
            {
                id: 2,
                label: "menuitems.homepage.list.datastatistics",
                icon: "ri-bar-chart-2-fill",
                link: 'dataStatistics'
            },
            // {
            //     id: 3,
            //     label: "menuitems.homepage.list.todonotification.text",
            //     badge: {
            //         variant: "warning",
            //         text: "menuitems.homepage.list.todonotification.badge"
            //     },
            //     icon: "ri-notification-3-fill",
            //     link: "#"
            // },
            // {
            //     id: 4,
            //     label: "menuitems.homepage.list.messagenotification.text",
            //     badge: {
            //         variant: "info",
            //         text: "menuitems.homepage.list.messagenotification.badge"
            //     },
            //     icon: "ri-message-2-fill",
            //     link: "#"
            // }
        ]
    },
    {
        id: 5,
        label: "menuitems.filingmanagement.text",
        icon: "ri-file-search-fill",
        link: "filesManagement"
    },
    {
        id: 6,
        label: "menuitems.workbench.text",
        icon: "ri-apps-fill",
        subItems: [
            {
                id: 7,
                label: "menuitems.workbench.list.personalmessage",
                icon: "ri-message-3-fill",
                link: "personalMessage"
            },
            {
                id: 8,
                label: "menuitems.workbench.list.messagemanagement",
                icon: "ri-chat-settings-fill",
                link: "messageManagement"
            },
            {
                id: 9,
                label: "menuitems.workbench.list.myborrowrecord",
                icon: "ri-file-list-2-fill",
                link: "myBorrowRecord"
            },
            {
                id: 10,
                label: "menuitems.workbench.list.borrowrecordmanagement",
                icon: "ri-file-settings-fill",
                link: "borrowRecordManagement"
            }
        ]
    },
    {
        id: 11,
        label: "menuitems.audit.text",
        icon: "ri-history-fill",
        subItems: [
            {
                id: 12,
                label: "menuitems.audit.list.filingaudit",
                icon: "ri-folder-4-fill",
                link: "filingAudit"
            },
            {
                id: 13,
                label: "menuitems.audit.list.fileaudit",
                icon: "ri-file-text-fill",
                link: "fileAudit"
            }
        ]
    },
    {
        id: 14,
        label: "menuitems.profile.text",
        icon: "ri-account-box-fill",
        subItems: [
            {
                id: 15,
                label: "menuitems.profile.list.basicsetting",
                icon: "ri-settings-5-fill",
                link: "basicSetting"
            },
            {
                id: 16,
                label: "menuitems.profile.list.securitysetting",
                icon: "ri-user-settings-fill",
                link: "securitySetting"
            }
        ]
    },
    {
        id: 17,
        label: "menuitems.usermanagement.text",
        icon: "ri-shield-user-fill",
        link: "userManagement"
    },
    {
        id: 18,
        label: "menuitems.rolemanagement.text",
        icon: "ri-map-pin-user-fill",
        link: "roleManagement"
    }
]