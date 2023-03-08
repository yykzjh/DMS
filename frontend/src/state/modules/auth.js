import { getFirebaseBackend } from '../../helpers/firebase/authUtils'
import {request} from '@/network/request'

export const state = {
    currentUser: JSON.parse(localStorage.getItem('user')?localStorage.getItem('user'):sessionStorage.getItem("user")),
    avatarChange: false,
}

export const mutations = {
    SET_CURRENT_USER(state, newValue) {
        state.currentUser = newValue
    },
    SET_AVATAR_CHANGE(state, newValue) {
        state.avatarChange = !state.avatarChange
    },

}

export const getters = {
    // Whether the user is currently logged in.
    loggedIn(state) {
        return !!state.currentUser
    },
}

export const actions = {
    // This is automatically run in `src/state/store.js` when the app
    // starts, along with any other actions named `init` in other modules.
    // eslint-disable-next-line no-unused-vars
    init({ state, dispatch }) {
        dispatch('validate')
    },

    // Logs in the current user.
    logIn({ commit, dispatch, getters }, { userid, password, requireRemenber=false} = {}) {
        // console.log(1111)
        sessionStorage.removeItem("user")
        localStorage.removeItem("user")
        // console.log(151515)
        return request({
            url: '/User/Login',
            method: "post",
            data: {
                userid: userid,
                pwd: password
            }
        }).then(res => {
            // console.log(2222)
            let data = res.data
            if(data['errcode']==0){
                commit('SET_CURRENT_USER', data['user'])
                sessionStorage.setItem("user", JSON.stringify(data['user']))
                if (requireRemenber) localStorage.setItem("user", JSON.stringify(data['user']))
            }
            return {
                errcode: data['errcode'],
                errmsg: data['errmsg']
            }
        }).catch(err => {
            return {
                errcode: 1,
                errmsg: "response error!"
            }
        })
    },

    // Logs out the current user.
    logOut({ commit }) {
        commit('SET_CURRENT_USER', null)
        sessionStorage.removeItem("user")
        localStorage.removeItem("user")
    },


    // register the user
    // eslint-disable-next-line no-unused-vars
    resetPassword({ commit, dispatch, getters }, { email } = {}) {
        if (getters.loggedIn) return dispatch('validate')

        return getFirebaseBackend().forgetPassword(email).then((response) => {
            const message = response.data
            return message
        });
    },


    validate({ commit, state }){
        return request({
            url: "/User/Validate",
            method: "get",
            params:{
                token:state.currentUser.token
            }
        }).then(res => {
            if (res.data.errcode != 0){
                sessionStorage.removeItem("user")
                localStorage.removeItem("user")
            }
            return res
        })
    }
}
