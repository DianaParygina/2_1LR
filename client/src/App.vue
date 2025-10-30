<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

</script>

<template>
  <div class="container"></div>
  <nav class="navbar navbar-expand-sm navbar-light bg-light px-4">
  <a class="navbar-brand" href="#">Сайтик</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavDropdown" aria-controls="navbarNavDropdown" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse justify-content-between" id="navbarNavDropdown">
    <ul class="navbar-nav">
      <li class="nav-item">
        <router-link class="nav-link" to="/"> Собаки</router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/breeds"> Породы</router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/owners"> Владельцы</router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/countries"> Страны</router-link>
      </li>
      <li class="nav-item">
        <router-link class="nav-link" to="/hobby"> Хобби</router-link>
      </li>
    </ul>

    <!-- <ul class="navbar-nav">
      <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
        Пользователь
        </a>
        <ul class="dropdown-menu">
          <li><a class="dropdown-item" href="/admin">Админка</a></li>
        </ul>
      </li>
    </ul> -->

    <ul class="navbar-nav">
      <li class="nav-item">
        <router-link class="nav-link" to="/login"> Vh </router-link>
      </li>
    </ul>
  </div>
</nav>
<router-view/>
</template>

<style scoped>

</style>