<script setup>
import {computed, ref, onBeforeMount} from 'vue';
import axios from "axios";
import Cookies from 'js-cookie';

const hobbies = ref({});
const hobbyToEdit = ref({});
const hobbyToAdd = ref({});

const loading = ref(false); 

async function fetchHobby(){
  const r = await axios.get("/api/hobby/");
  console.log(r.data)
  hobbies.value = r.data;
}

async function onLoadClickForHobby(){
  await fetchHobby()
}


async function onDogClickForHobby(){
  await axios.post("/api/hobby/", {
    ...hobbyToAdd.value,
  });
  await fetchHobby(); // переподтягиваю
  hobbyToAdd.value = {};
}

async function onRemoveClickForHobby(hobby) {
  await axios.delete(`/api/hobby/${hobby.id}/`);
  await fetchHobby();
}


async function onHobbyEditClick(hobby) {
  hobbyToEdit.value = { ...hobby }; 
}

async function onUpdateHobby() {
  await axios.put(`/api/hobby/${hobbyToEdit.value.id}/`, {
    ...hobbyToEdit.value,
  });
  await fetchHobby(); 
}


const hobbyStats = ref(null);


async function fetchHobbyStats() {
    const r = await axios.get("/api/hobby/stats/");
    hobbyStats.value = r.data;
}



onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  fetchHobbyStats();
  fetchHobby();
})

</script>

<template>
    <div><br>
    <button class="btn btn-primary ms-4" @click="onLoadClickForHobby">Загрузить хобби собак</button>

    <form @submit.prevent.stop="onDogClickForHobby">
      <div class="row m-1">
        <div class="col-5 ms-1 m-2">
        <div class="form-floating">
            <input
              type="text"
              class="form-control"
              v-model="hobbyToAdd.name_hobby"
              required
            />
            <label for="floatingInput">Добавим хобби</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <button class="btn btn-primary">
            Добавить
          </button>
        </div>
      </div>
    </form>


    <div class="row border align-items-center m-2 rounded" v-for="hobby in hobbies">
      <div class="col-10">
        <div class="country-item">
          {{ hobby.name_hobby }}
        </div>
      </div>
      <div class="col">
        <button class="btn btn-success" @click="onHobbyEditClick(hobby)" data-bs-toggle="modal"
          data-bs-target="#editDogModal5">
          <i class="bi bi-pen-fill"></i>
        </button>
      </div>
      <div class="col">
        <button class="btn btn-danger" @click="onRemoveClickForHobby(hobby)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>

    <div class="modal fade" id="editDogModal5" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Редактировать хобби
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col">
                <div class="form-floating">
                  <input type="text" class="form-control" v-model="hobbyToEdit.name_hobby" />
                  <label for="floatingInput">Хобби</label>
                </div>
              </div>
              <div class="col">
        </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button type="button" class="btn btn-primary" @click="onUpdateHobby" data-bs-dismiss="modal">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="hobbyStats" class="m-3">
      <h3>Статистика по хобби:</h3>
      <p>Количество: {{ hobbyStats.count }}</p>
      <p>Среднее id: {{ hobbyStats.avg }}</p>
      <p>Максимальное id: {{ hobbyStats.max }}</p>
      <p>Минимальное id: {{ hobbyStats.min }}</p>
    </div>
</template>


<style scoped>
</style>
