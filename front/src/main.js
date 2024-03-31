import { createApp, h } from 'vue'
import './style.css'
import Home from './components/Home.vue'

const routes = {
    '/': Home
}

const SimpleRouter = {
    data: () => ({
        currentRoute: window.location.pathname
    }),

    computed: {
        CurrentComponent() {
            return routes[this.currentRoute] || NotFoundComponent
        }
    },

    render() {
        return h(this.CurrentComponent)
    }
}

createApp(SimpleRouter).mount('#app')
