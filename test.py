import datetime

from pip._vendor import requests
from pip._vendor.requests import post, get

print(get('http://localhost:8080/'))
print(post('http://localhost:8080/', json={
    'msg': 'asdfghyrtedfx'
}))

print(post('http://localhost:8080/couriers', json=
           {
               "data": [
                   {
                       "courier_id": 1,
                       "courier_type": "foot",
                       "regions": [1, 12, 22],
                       "working_hours": ["11:35-14:05", "09:00-11:00"]
                   },
                   {
                       "courier_id": 2,
                       "courier_type": "bike",
                       "regions": [22],
                       "working_hours": ["09:00-18:00"]
                   },
                   {
                       "courier_id": 3,
                       "courier_type": "car",
                       "regions": [12, 22, 23, 33],
                       "working_hours": []
                   },

               ]
           }).json())

print(post('http://localhost:8080/couriers', json=
           {
               "data": [
                   {
                       "courier_id": 1,
                       "courier_type": "foot",
                       "regions": [1, 12, 22],
                       "cities": [4, 12, 22],
                       "working_hours": ["11:35-14:05", "09:00-11:00"]
                   },
                   {
                       "courier_id": 2,
                       "regions": [22],
                       "working_hours": ["09:00-18:00"]
                   },
                   {
                       "courier_id": 3,
                   },
                   {
                       "courier_id": 4,
                       "courier_type": "car",
                       "regions": [12, 22, 23, 33],
                       "working_hours": []
                   },
               ]
           }).json())

print(requests.patch('http://localhost:8080/couriers/1', json=
{
    'regions': [1, 2, 3]
}).json())

print(requests.post('http://localhost:8080/orders', json=
{
    "data": [
        {
            "order_id": 1,
            "weight": 0.23,
            "region": 12,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 2,
            "weight": 15,
            "region": 1,
            "delivery_hours": ["09:00-18:00"]
        },
        {
            "order_id": 3,
            "weight": 0.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        },
        {
            "order_id": 4,
            "weight": 20.01,
            "region": 22,
            "delivery_hours": ["09:00-12:00", "16:00-21:30"]
        }]
}).json())

print(requests.post('http://localhost:8080/orders/assign', json=
{
    'courier_id': 2
}).json())

print(requests.patch('http://localhost:8080/couriers/1', json=
{
    'regions': [1, 2, 3]
}).json())

print(requests.post('http://localhost:8080/orders/complete', json=
{
    "courier_id": 2,
    "order_id": 3,
    "complete_time": "2021-03-28T16:20:15.089Z"
}).json())


print(requests.get('http://localhost:8080/couriers/2').json())
