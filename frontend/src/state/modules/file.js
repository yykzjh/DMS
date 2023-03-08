export const state = {
    showFilesInfo: {
        level: 0,
        id: 0,
        page: 1,
        pageSize: 5,
        showfileDetails: false,
        havePermission: false,
        fileName: "",
        creator: "",
        belongType:"",
        fileHaveChange: false,
    },
    openFolder: false,
    filingHaveChange: false,
}

export const mutations = {
    SET_SHOW_FILES_INFO(state, newObj) {
        state.showFilesInfo = newObj
    },
    SET_FILE_CHANGE(state, newVal) {
        state.showFilesInfo.fileHaveChange = newVal
    },
    SET_OPEN_FOLDER(state, newVal) {
        state.openFolder = newVal
    }
}