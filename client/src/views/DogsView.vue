<script setup>
import { computed, ref, onBeforeMount, watch } from 'vue';
import axios from "axios";
import Cookies from 'js-cookie';
import { storeToRefs } from 'pinia';
import useUserState from '../../stores/userStore';

const dogs = ref([]);
const dogToAdd = ref({});
const dogToEdit = ref({});
const dogsPicturesRef = ref({});
const dogsEditPicturesRef = ref({});
const dogAddImageUrl = ref();
const dogEditImageUrl = ref();
const showModal = ref(false);
const selectedImage = ref(null);

const user = ref([]);


const userStore = useUserState();
const {
  isAuthenticated,
  userName,
  userId,
  owner
} = storeToRefs(userStore);


const breed = ref([]);
// const owner = ref([]);
const country = ref([]);
const hobby = ref([]);

const selectedOwnerId = ref(null);
const loading = ref(false);

async function fetchDogs() {
  loading.value = true;
  const params = {
    user_id: selectedOwnerId.value,
    name: dogNameFilter.value,
    'breed__name': dogBreedFilter.value,
    'country__country': dogCountryFilter.value,
    'hobby__name_hobby': dogHobbyFilter.value,
  };

  // Удаляем пустые параметры из запроса
  for (const key in params) {
    if (params[key] === '') {
      delete params[key];
    }
  }

  const r = await axios.get("/api/dogs/", { params });
  dogs.value = r.data;
  loading.value = false;
}

async function fetchBreeds() {
  const r = await axios.get("/api/breed/");
  console.log(r.data)
  breed.value = r.data;
}

async function fetchOwner() {
  const r = await axios.get("/api/owner/");
  console.log(r.data)
  owner.value = r.data;
}

async function fetchHobby() {
  const r = await axios.get("/api/hobby/");
  console.log(r.data)
  hobby.value = r.data;
}

async function fetchCountry() {
  const r = await axios.get("/api/country/");
  console.log(r.data)
  country.value = r.data;
}

async function fetchUsers() {
  // const r = await axios.get("/api/users/info/");
  // console.log(r.data)
  // users.value = r.data;
}



async function dogsAddPictureChange() {
  dogAddImageUrl.value = URL.createObjectURL(dogsPicturesRef.value.files[0])
}

async function dogsEditPictureChange() {
  dogEditImageUrl.value = URL.createObjectURL(dogsEditPicturesRef.value.files[0])
}

async function onLoadClick() {
  await fetchDogs()
}



async function onDogAdd() {
  const formData = new FormData();

  formData.append('picture', dogsPicturesRef.value.files[0]);

  formData.set('name', dogToAdd.value.name)
  formData.set('breed', dogToAdd.value.breed);
  formData.set('owner', dogToAdd.value.owner);
  formData.set('country', dogToAdd.value.country);
  formData.set('hobby', dogToAdd.value.hobby);

  await axios.post("/api/dogs/", formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchDogs(); // переподтягиваю
  // dogToAdd.value = {};
}


async function onRemoveClick(dog) {
  await axios.delete(`/api/dogs/${dog.id}/`);
  await fetchDogs();
}



async function onDogEditClick(dog) {
  dogToEdit.value = {
    ...dog,
    breed: dog.breed.id,
    owner: dog.owner.id,
    country: dog.country.id,
    hobby: dog.hobby.id,
  };
}


async function onUpdateDog() {
  const formData = new FormData();

  if (dogsEditPicturesRef.value.files[0]) {
    formData.append('picture', dogsEditPicturesRef.value.files[0]);
  }

  dogEditImageUrl.value = null;
  formData.set('name', dogToEdit.value.name)
  formData.set('breed', dogToEdit.value.breed)
  formData.set('owner', dogToEdit.value.owner)
  formData.set('country', dogToEdit.value.country)
  formData.set('hobby', dogToEdit.value.hobby)

  await axios.put(`/api/dogs/${dogToEdit.value.id}/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
  await fetchDogs(); // переподтягиваю
}





const dogStats = ref(null);
const breedStats = ref(null);
const ownerStats = ref(null);
const countryStats = ref(null);
const hobbyStats = ref(null);


async function fetchDogStats() {
  const r = await axios.get("/api/dogs/stats/", {
    params: {
      user_id: selectedOwnerId.value
    }
  });
  dogStats.value = r.data;
}








onBeforeMount(() => {
  axios.defaults.headers.common['X-CSRFToken'] = Cookies.get("csrftoken");

  userStore.fetchUser();
  userStore.fetchOwner();
  fetchDogs();
  fetchBreeds();
  // fetchOwner();
  fetchCountry();
  fetchHobby();
  fetchDogStats();
  fetchUsers();
})

watch(selectedOwnerId, () => {
  fetchDogs();
  fetchDogStats();
});

const dogNameFilter = ref('');
const dogBreedFilter = ref('');
const dogCountryFilter = ref('');
const dogHobbyFilter = ref('');



async function exportToExcel() {
    try {
        const response = await axios.get('/api/dogs/export/', {
            params: {
                user_id: selectedOwnerId.value,
                name: dogNameFilter.value,
                'breed__name': dogBreedFilter.value,
                'country__country': dogCountryFilter.value,
                'hobby__name_hobby': dogHobbyFilter.value,
            },
            responseType: 'blob', 
        });

        console.log(response.data)

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'dogs.xlsx');
        document.body.appendChild(link);
        link.click();
  } catch (error) {
        console.error("Ошибка при экспорте:", error);
    }
}

</script>

<template>

  <button @click="exportToExcel" class="btn btn-success m-4">Экспорт в Excel</button>


  <div v-if="owner">
    <div class="row m-1">
      <div class="col-2 m-1">
        <div class="form-floating">
          <select name="" id="" class="form-select" v-model="selectedOwnerId">
            <option value="">Все владельцы</option>
            <option :value="u.id" v-for="u in owner">{{ u.first_name }}</option>
          </select>
          <label for="floatingInput">Пользователь</label>
        </div>
      </div>
      <div class="col-2 m-1">
        <div class="form-floating">
          <input type="text" class="form-control" v-model="dogNameFilter" @input="fetchDogs" />
          <label for="floatingInput">Имя собаки</label>
        </div>
      </div>
      <div class="col-2 m-1">
        <div class="form-floating">
          <select name="" id="" class="form-select" v-model="dogBreedFilter" @change="fetchDogs">
            <option value="">Все породы</option>
            <option :value="b.name" v-for="b in breed">{{ b.name }}</option>
          </select>
          <label for="floatingInput">Порода</label>
        </div>
      </div>
      <div class="col-2 m-1">
        <div class="form-floating">
          <select name="" id="" class="form-select" v-model="dogCountryFilter" @change="fetchDogs">
            <option value="">Все страны</option>
            <option :value="c.country" v-for="c in country">{{ c.country }}</option>
          </select>
          <label for="floatingInput">Страна</label>
        </div>
      </div>
      <div class="col-2 m-1">
        <div class="form-floating">
          <select name="" id="" class="form-select" v-model="dogHobbyFilter" @change="fetchDogs">
            <option value="">Все хобби</option>
            <option :value="h.name_hobby" v-for="h in hobby">{{ h.name_hobby }}</option>
          </select>
          <label for="floatingInput">Хобби</label>
        </div>
      </div>
      <!-- <div class="col-2 m-1">
        <button @click="onLoadClick" class="btn btn-primary m-1">Загрузить собак</button>
      </div> -->
    </div>


    <form @submit.prevent.stop="onDogAdd">

      <div class="row m-1">
        <div class="col-5 ms-1 m-2">
          <div class="form-floating">
            <input type="text" class="form-control" v-model="dogToAdd.name" required />
            <label for="floatingInput">Имя</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <div class="form-floating">
            <select name="" id="" class="form-select" v-model="dogToAdd.breed">
              <option :value="b.id" v-for="b in breed">{{ b.name }}</option>
            </select>
            <label for="floatingInput">Порода</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <input class="form-control" type="file" ref="dogsPicturesRef" @change="dogsAddPictureChange">
        </div>
        <div class="col-5 ms-1 m-2">
          <img :src="dogAddImageUrl" style="max-height:  60px;" alt="">
        </div>
        <div class="col-5 ms-1 m-2">
          <div class="form-floating">
            <select name="" id="" class="form-select" v-model="dogToAdd.owner">
              <option :value="o.id" v-for="o in owner">{{ o.first_name }} {{ o.last_name }}</option>
            </select>
            <label for="floatingInput">Хозяин</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <div class="form-floating">
            <select name="" id="" class="form-select" v-model="dogToAdd.country">
              <option :value="c.id" v-for="c in country">{{ c.country }}</option>
            </select>
            <label for="floatingInput">Страна</label>
          </div>
        </div>
        <div class="col-5 ms-1 m-2">
          <div class="form-floating">
            <select name="" id="" class="form-select" v-model="dogToAdd.hobby">
              <option :value="h.id" v-for="h in hobby">{{ h.name_hobby }}</option>
            </select>
            <label for="floatingInput">Хобби</label>
          </div>
        </div>
        <div class="col-auto">
          <button class="btn btn-primary m-2">
            Добавить
          </button>
        </div>
      </div>
    </form>





    <div class="row border align-items-center m-2 rounded" v-for="dog in dogs">
      <div class="col-9">
        <div class="dog-item">
          {{ dog.name }}
        </div>
      </div>
      <div class="col-1 m-1">
        <div v-show="dog.picture" @click="showModal = true; selectedImage = dog.picture">
          <img :src="dog.picture" style="max-height: 60px; border-radius: 10%;" data-bs-toggle="modal"
            data-bs-target="#pictureDogModal">
        </div>
      </div>
      <div class="col">
        <button class="btn btn-success" @click="onDogEditClick(dog)" data-bs-toggle="modal"
          data-bs-target="#editDogModal">
          <i class="bi bi-pen-fill"></i>
        </button>
      </div>
      <div class="col">
        <button class="btn btn-danger" @click="onRemoveClick(dog)">
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>



    <div class="modal fade" id="editDogModal" tabindex="-1"
      @hidden.bs.modal="dogsEditPicturesRef.value = null; dogEditImageUrl.value = null;">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h1 class="modal-title fs-5" id="exampleModalLabel">
              Редактировать собаку
            </h1>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="row">
              <div class="col-5 ms-1 m-2">
                <div class="form-floating">
                  <input type="text" class="form-control" v-model="dogToEdit.name" />
                  <label for="floatingInput">Имя</label>
                </div>
              </div>
              <div class="col-5 ms-1 m-2">
                <div class="form-floating">
                  <select name="" id="" class="form-select" v-model="dogToEdit.breed">
                    <option :value="b.id" v-for="b in breed">{{ b.name }}</option>
                  </select>
                  <label for="floatingInput">Порода</label>
                </div>
              </div>
              <div class="col-5 ms-1 m-2">
                <input class="form-control" type="file" ref="dogsEditPicturesRef" @change="dogsEditPictureChange">
              </div>
              <div class="col-5 ms-1 m-2">
                <div class="form-floating">
                  <select name="" id="" class="form-select" v-model="dogToEdit.owner">
                    <option :value="o.id" v-for="o in owner">{{ o.first_name }} {{ o.last_name }}</option>
                  </select>
                  <label for="floatingInput">Хозяин</label>
                </div>
              </div>
              <div class="col-5 ms-1 m-2">
                <div class="form-floating">
                  <select name="" id="" class="form-select" v-model="dogToEdit.country">
                    <option :value="c.id" v-for="c in country">{{ c.country }}</option>
                  </select>
                  <label for="floatingInput">Страна</label>
                </div>
              </div>
              <div class="col-5 ms-1 m-2">
                <div class="form-floating">
                  <select name="" id="" class="form-select" v-model="dogToEdit.hobby">
                    <option :value="h.id" v-for="h in hobby">{{ h.name_hobby }}</option>
                  </select>
                  <label for="floatingInput">Хобби</label>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
              Close
            </button>
            <button type="button" class="btn btn-primary" @click="onUpdateDog" data-bs-dismiss="modal">
              Сохранить
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div v-if="isAuthenticated">
    <div v-if="dogStats" class="m-3">
      <h3>Статистика по собакам:</h3>
      <p>Количество: {{ dogStats.count }}</p>
      <p>Среднее id: {{ dogStats.avg }}</p>
      <p>Максимальное id: {{ dogStats.max }}</p>
      <p>Минимальное id: {{ dogStats.min }}</p>
    </div>
  </div>



  <div class="modal fade" id="pictureDogModal" tabindex="-1">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
        </div>
        <div class="modal-body">
          <div class="row">
            <img :src="selectedImage" style="width: 100%; display: block; margin-left: auto; margin-right: auto">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped></style>
