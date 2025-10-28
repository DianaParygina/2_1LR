<script setup>
import {computed, ref, onBeforeMount} from 'vue';
import axios from "axios";
import Cookies from 'js-cookie';

const countries = ref({});
const countryToEdit = ref({});
const countryToAdd = ref({});

const loading = ref(false); 

async function fetchCountry(){
  const r = await axios.get("/api/country/");
  console.log(r.data)
  countries.value = r.data;
}

async function onLoadClickForBreedCountry(){
  await fetchCountry()
}

async function onDogClickForCountry(){
  await axios.post("/api/country/", {
    ...countryToAdd.value,
  });
  await fetchCountry(); // переподтягиваю
  countryToAdd.value = {};
}

async function onRemoveClickForCountry(country) {
  await axios.delete(`/api/country/${country.id}/`);
  await fetchCountry();
}


async function onCountryEditClick(country) {
  countryToEdit.value = { ...country }; 
}

async function onUpdateCountry() {
  await axios.put(`/api/country/${countryToEdit.value.id}/`, {
    ...countryToEdit.value,
  });
  await fetchCountry(); 
}


const countryStats = ref(null);

async function fetchCountryStats() {
    const r = await axios.get("/api/country/stats/");
    countryStats.value = r.data;
}



onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");
  fetchCountryStats();
  fetchCountry();
})

</script>

<template>
  <div><br>
    <button class="btn btn-primary ms-4" @click="onLoadClickForBreedCountry">Загрузить страны собак</button>

    <form @submit.prevent.stop="onDogClickForCountry">
      <div class="row m-1">
        <div class="col-5 ms-1 m-2">
        <div class="form-floating">
            <input
              type="text"
              class="form-control"
              v-model="countryToAdd.country"
              required
            />
            <label for="floatingInput">Добавим страну</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <button class="btn btn-primary">
            Добавить
          </button>
        </div>
      </div>
    </form>


    <div class="row border align-items-center m-2 rounded" v-for="country in countries">
      <div class="col-10">
        <div class="country-item">
          {{ country.country }}
        </div>
      </div>
      <div class="col">
        <button class="btn btn-success" @click="onCountryEditClick(country)" data-bs-toggle="modal"
          data-bs-target="#editDogModal4">
          <i class="bi bi-pen-fill"></i>
        </button>
      </div>
      <div class="col">
        <button class="btn btn-danger" @click="onRemoveClickForCountry(country)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>


    <div class="modal fade" id="editDogModal4" tabindex="-1">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Редактировать страну
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col">
                <div class="form-floating">
                  <input type="text" class="form-control" v-model="countryToEdit.country" />
                  <label for="floatingInput">Страна</label>
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
            <button type="button" class="btn btn-primary" @click="onUpdateCountry" data-bs-dismiss="modal">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="countryStats">
    <div v-if="countryStats" class="m-3">
      <h3>Статистика по странам:</h3>
      <p>Количество: {{ countryStats.count }}</p>
      <p>Среднее id: {{ countryStats.avg }}</p>
      <p>Максимальное id: {{ countryStats.max }}</p>
      <p>Минимальное id: {{ countryStats.min }}</p>
      </div>
    </div>
</template>


<style scoped>
</style>
