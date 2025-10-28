from django.core.management.base import BaseCommand

from faker import Faker

from dogs.models import Dog, Owner


class Command(BaseCommand):
    def handle(self, *args, **options):
        fake = Faker(['ru_RU'])
        dog_names = [
    'Бобик', 'Шарик', 'Тузик', 'Рекс', 'Мухтар', 'Джесси', 'Белла', 'Люси', 'Макс', 'Чарли', 'Бадди', 'Роки', 'Джек', 'Мила', 'Лео', 
    'Luna', 'Daisy', 'Lola', 'Sadie', 'Molly', 'Bailey', 'Maggie', 'Sophie', 'Coco', 'Roxy', 'Gracie', 'Ruby', 'Penny', 'Willow', 'Nala', 
    'Simba', 'Zeus', 'Apollo', 'Thor', 'Loki', 'Milo', 'Oliver', 'Teddy', 'Oscar', 'Archie', 'Bruno', 'Duke', 'Bear', 'Gus', 'Jasper', 
    'Toby', 'Finn', 'Murphy', 'Winston', 'Harley', 'Ace'
    ]
        dog_picture = [
            'dogs/ab7d4dbd-c726-470b-83e6-6191cb5428f5.jpg', 
            'dogs/photo_5226442168477016573_y.jpg',
            'dogs/photo_5228782062364909984_y.jpg',
            'dogs/photo_5424876838737537889_y.jpg',
            'dogs/photo_5193036724597549348_x.jpg',
            'dogs/photo_5206339058652012976_y.jpg',
            'dogs/photo_5228782062364909979_y.jpg',
            'dogs/photo_5228782062364909982_y.jpg',
            'dogs/photo_5228782062364909983_x.jpg',
            'dogs/photo_5228782062364909987_m.jpg',
            'dogs/photo_5453922787732350059_x.jpg',
            'dogs/photo_5471987600567952261_x.jpg',
        ]

        for _ in range(1000):
            Dog.objects.create(
                name=fake.random_element(elements=dog_names),
                picture=fake.random_element(elements=dog_picture)
            )
        for _ in range(1000):
            Owner.objects.create(
                first_name=fake.name()
            )  
            