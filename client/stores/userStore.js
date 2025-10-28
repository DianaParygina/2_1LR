import { onBeforeMount, ref } from "vue";
import axios from "axios";
import { defineStore } from "pinia";


const useUserState = defineStore("UserStore", ()=>{
    const isAuthenticated = ref(false);
    const userName = ref("");
    const userId = ref();
    const owner = ref()

    async function fetchUser() {
        const r = await axios.get("/api/user/info/")
        console.log(r.data)
        isAuthenticated.value = r.data.is_authenticated;
        userName.value = r.data.userName;
        userId.value = r.data.userId;
    }

    async function fetchOwner() {
        // loading.value = true;
        const r = await axios.get("/api/owner/");
        console.log(r.data)
        owner.value = r.data;
        // loading.value = false;
      }

    onBeforeMount(()=> {
        fetchUser();
    })

    return{
        isAuthenticated,
        userName,
        userId,
        fetchUser,
        fetchOwner,
        owner,
    }
})

export default useUserState