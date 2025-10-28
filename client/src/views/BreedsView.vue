<script setup>
import {computed, ref, onBeforeMount} from 'vue';
import axios from "axios";
import Cookies from 'js-cookie';
import useUserState from '../../stores/userStore';

const userStore = useUserState();

const breeds = ref({});
const breedToEdit = ref({});
const breedToAdd = ref({});

const loading = ref(false); 


async function fetchBreeds(){
  const r = await axios.get("/api/breed/");
  console.log(r.data)
  breeds.value = r.data;
}


async function onLoadClickForBreed(){
  await fetchBreeds()
}



async function onDogClickForBreeds(){
  await axios.post("/api/breed/", {
    ...breedToAdd.value,
  });
  await fetchBreeds(); // переподтягиваю
  breedToAdd.value = {};
}

async function onRemoveClickForBreed(breed) {
  await axios.delete(`/api/breed/${breed.id}/`);
  await fetchBreeds();
}


async function onBreedEditClick(breed) {
  breedToEdit.value = { ...breed }; 
}


async function onUpdateBreed() {
  await axios.put(`/api/breed/${breedToEdit.value.id}/`, {
    ...breedToEdit.value,
  });
  await fetchBreeds(); 
}


const breedStats = ref(null);

async function fetchBreedStats() {
    const r = await axios.get("/api/breed/stats/");
    breedStats.value = r.data;
}


onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  fetchBreedStats();
  fetchBreeds();
})


</script>

<template>
  <div><br>
    <button class="btn btn-primary ms-4" @click="onLoadClickForBreed">Загрузить породы собак</button>

    
    <form @submit.prevent.stop="onDogClickForBreeds">
      <div class="row m-1">
        <div class="col-3 m-2">
        <div class="form-floating">
            <input
              type="text"
              class="form-control"
              v-model="breedToAdd.name"
              required
            />
            <label for="floatingInput">Добавить породу</label>
          </div>
        </div>
        <div class="col-3 m-3">
          <button class="btn btn-primary">
            Добавить
          </button>
        </div>
      </div>
    </form>  


    <div class="row border align-items-center m-2 rounded" v-for="breed in breeds">
      <div class="col-10">
        <div class="breed-item">
          {{ breed.name }}
        </div>
      </div>
      <div class="col">
        <button class="btn btn-success" @click="onBreedEditClick(breed)" data-bs-toggle="modal"
          data-bs-target="#editDogModal2">
          <i class="bi bi-pen-fill"></i>
        </button>
      </div>
      <div class="col">
        <button class="btn btn-danger" @click="onRemoveClickForBreed(breed)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>



    <div class="modal fade" id="editDogModal2" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Редактировать породу
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col">
                <div class="form-floating">
                  <input type="text" class="form-control" v-model="breedToEdit.name" />
                  <label for="floatingInput">Порода</label>
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
            <button type="button" class="btn btn-primary" @click="onUpdateBreed" data-bs-dismiss="modal">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div> 
  

    <div v-if="breedStats" class="m-3">
      <h3>Статистика по пародам:</h3>
      <p>Количество: {{ breedStats.count }}</p>
      <p>Среднее id: {{ breedStats.avg }}</p>
      <p>Максимальное id: {{ breedStats.max }}</p>
      <p>Минимальное id: {{ breedStats.min }}</p>
    </div>

    
       
       
</template>


<style scoped>
</style>
