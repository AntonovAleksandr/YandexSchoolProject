import datetime
import unittest
import requests
from src import db_session

path_to_server = "127.0.0.1:5002"
db_session.global_init("/src/data_base/delivery_data_base.sqlite")

class UnitTest(unittest.TestCase):
    def test_couriers(self):
        res = requests.post('http://localhost:5002/couriers', json=
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
           }).json()

        self.assertEqual(res["couriers"][0]['id'], 1, "Should be 1")
        self.assertEqual(res["couriers"][1]['id'], 2, "Should be 2")
        self.assertEqual(res["couriers"][2]['id'], 3, "Should be 3")

        def test_orders(self):
            res = requests.post(f"http://{path_to_server}/orders", json={
                "data": [
                    {
                        "order_id": 1,
                        "weight": 0.23,
                        "region": 12,
                        "delivery_hours": ["09:00-18:00"]
                    },
                    {
                        "order_id": 5,
                        "weight": 0.57,
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
                        "weight": 0.22,
                        "region": 11,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    },
                    {
                        "order_id": 6,
                        "weight": 0.88,
                        "region": 33,
                        "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    }
                ]
            }).json()

            self.assertEqual(res["orders"][0]['id'], 1, "Should be 1")
            self.assertEqual(res["orders"][1]['id'], 5, "Should be 5")
            self.assertEqual(res["orders"][2]['id'], 2, "Should be 2")
            self.assertEqual(res["orders"][3]['id'], 3, "Should be 3")
            self.assertEqual(res["orders"][4]['id'], 4, "Should be 4")
            self.assertEqual(res["orders"][5]['id'], 6, "Should be 6")


class Test(unittest.TestCase):
    def test_couriers_validation_error(self):
        res = requests.post(f"http://{path_to_server}/couriers", json={
            "data": [
                {
                    "courier_id": 1,
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                }
            ]
        })
        self.assertEqual(res.json()["validation_error"]['couriers'][0]['id'], 1, "Should be 1")
        self.assertEqual(res.status_code, 400, "Should be 400")


    def test_patch_courier(self):
        res = requests.patch(f"http://{path_to_server}/couriers/2", json={
            "regions": [11, 33, 2]
        }).json()

        self.assertEqual(res['regions'], [11, 33, 2], "Should be [11, 33, 2]")

    def test_patch_courier_error(self):
        res = requests.patch(f"http://{path_to_server}/couriers/2", json={
            "courier_id": 11
        })

        self.assertEqual(res.status_code, 400, "Should be 400")



    def test_orders_error(self):
        res = requests.post(f"http://{path_to_server}/orders", json={
            "data": [
                {
                    "order_id": 1,
                    "weight": 0.23,
                    "andyabdya": 1,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                },
            ]
        })

        self.assertEqual(res.json()["validation_error"]['orders'][0]['id'], 1, "Should be 1")
        self.assertEqual(res.status_code, 400, "Should be 400")

        res = requests.post(f"http://{path_to_server}/orders", json={
            "data": [
                {
                    "order_id": 1,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                }
            ]
        })

        self.assertEqual(res.json()["validation_error"]['orders'][0]['id'], 1, "Should be 1")
        self.assertEqual(res.status_code, 400, "Should be 400")

    def test_courier_assign(self):
        res = requests.post(f"http://{path_to_server}/orders/assign", json={'courier_id': 2}).json()
        self.assertEqual(res['orders'][0]['id'], 4, "Should be 4")
        self.assertEqual(res['orders'][1]['id'], 6, "Should be 6")
        self.assertEqual("assign_time" in res, True, "Should be True")

        res = requests.post(f"http://{path_to_server}/orders/assign", json={'courier_id': 1}).json()
        self.assertEqual(res['orders'][0]['id'], 1, "Should be 1")
        self.assertEqual(res['orders'][1]['id'], 3, "Should be 3")
        self.assertEqual(res['orders'][2]['id'], 5, "Should be 5")
        self.assertEqual("assign_time" in res, True, "Should be True")

    def test_courier_order_complete(self):
        res = requests.post(f"http://{path_to_server}/orders/complete", json=
        {
            "courier_id": 1,
            "order_id": 3,
            "complete_time": (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }).json()

        self.assertEqual(res['order_id'], 3, "Should be 3")

    def test_courier_order_complete_error(self):
        res = requests.post(f"http://{path_to_server}/orders/complete", json=
        {
            "courier_id": 1,
            "order_id": 33,
            "complete_time": (datetime.datetime.now() + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        })

        self.assertEqual(res.status_code, 400, "Should be 400")

    def test_couriers_statistic(self):
        res = requests.get(f'http://{path_to_server}/couriers/1').json()
        self.assertEqual("rating" in res, True, "Should be True")
        self.assertEqual("earnings" in res, True, "Should be True")


if __name__ == '__main__':
    unittest.main()