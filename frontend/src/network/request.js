import axios from 'axios'

export function request(config){
    // 1. 创建axios的实例
    const instance = axios.create({
        baseURL: 'http://localhost:8088',
        timeout: 10000,
        headers: {
            'Content-Type': 'application/json'
        }
    })

    instance.interceptors.request.use(config => {
        config.headers.Authorization = JSON.parse(window.sessionStorage.getItem("user"))==null?null:JSON.parse(window.sessionStorage.getItem("user")).token
        return config
    }, err => {
        console.log(err)
    }) 

    instance.interceptors.response.use(res => {
        if (res.status == 403) alert("登录超时，请刷新页面重新登录！")
        return res
    })

    return instance(config)
}