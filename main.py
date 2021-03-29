from datetime import datetime

from flask import Flask, request
import db_session
from entities.courier import Courier
from entities.delivery_hour import DeliveryHour
from entities.order import Order
from additional_func import make_resp, dict_has_keys, keys_is_has_dict_keys, is_time_in_times
from properties import WEIGHT, DEFAULT_COMPLETE_TIME
from entities.orders_execution import OrderExecution
from entities.region import Region
from entities.working_hour import WorkingHour
from waitress import serve

app = Flask(__name__)
app.config['SECRET_KEY'] = 'flag_is_here'


@app.route('/couriers', methods=['POST'])
def post_couriers():
    session = db_session.create_session()
    get_data = request.json
    validation_error = []
    ids = []
    valid_keys = ('courier_id', 'courier_type', 'regions', 'working_hours')
    for i in get_data['data']:
        if not dict_has_keys(i, valid_keys) or \
                not keys_is_has_dict_keys(i, valid_keys):
            validation_error.append({"id": i['courier_id']})
        else:
            ids.append({"id": i['courier_id']})
            regions = []
            for j in i['regions']:
                region = Region(
                    region_number=j,
                    courier_id=i['courier_id']
                )
                regions.append(region)
            working_hours = []
            for j in i['working_hours']:
                working_hour = WorkingHour(
                    courier_id=i['courier_id']
                )
                working_hour.set_working_hour(j)
                working_hours.append(working_hour)
            courier = Courier(
                id=i['courier_id'],
                type=i['courier_type'],
                regions=regions,
                working_hours=working_hours
            )
            session.add(courier)
            session.commit()
    if validation_error:
        return make_resp({'validation_error': {"couriers": validation_error}}, 400)
    else:
        return make_resp({"couriers": ids}, 201)


@app.route('/couriers/<int:id>', methods=['PATCH'])
def patch_update_courier_by_id(id):
    session = db_session.create_session()
    get_data = request.json
    valid_keys = ('courier_id', 'courier_type', 'regions', 'working_hours')
    if not keys_is_has_dict_keys(get_data, valid_keys):
        return make_resp('', 400)
    courier = session.query(Courier).filter(Courier.id == id).first()
    if courier:
        if 'courier_type' in get_data.keys():
            session.query(Courier).filter(Courier.id == id).update({'courier_type': get_data['courier_type']})
        if 'regions' in get_data.keys():
            courier.update_regions(get_data['regions'], session)
        if 'working_hours' in get_data.keys():
            courier.update_working_hours(get_data['working_hours'], session)
        courier = session.query(Courier).filter(Courier.id == id).first()
        courier_type = courier.type
        regions = [i.region_number for i in courier.regions]
        working_hours = [i.working_hour for i in courier.working_hours]
        courier_orders = courier.orders
        for i in courier_orders:
            if i.order.region_number not in regions or not is_time_in_times(courier.working_hours,
                                                                            i.order.delivery_hours[0]):
                i.order.is_taken = False
                session.query(OrderExecution).filter(OrderExecution.order_id == i.id).delete()
        session.commit()
        return make_resp({"courier_id": id,
                          "courier_type": courier_type,
                          "regions": regions,
                          "working_hours": working_hours}, 200)
    else:
        return make_resp('', 400)


@app.route('/orders', methods=['POST'])
def post_orders():
    session = db_session.create_session()
    data = request.json
    validation_error = []
    ids = []
    valid_keys = ('order_id', 'weight', 'region', 'delivery_hours')
    for i in data['data']:
        if not dict_has_keys(i, valid_keys) or \
                not keys_is_has_dict_keys(i, valid_keys):
            validation_error.append({"id": i['order_id']})
        else:
            order = session.query(Order).filter(Order.id == i['order_id']).first()
            if order:
                session.delete(order)
                session.commit()
            ids.append({"id": i['order_id']})
            delivery_hours = []
            for j in i['delivery_hours']:
                delivery_hour = DeliveryHour(
                    order_id=i['order_id']
                )
                delivery_hour.set_delivery_hour(j)
                delivery_hours.append(delivery_hour)
            order = Order(
                id=i['order_id'],
                weight=i['weight'],
                region_number=i['region'],
                delivery_hours=delivery_hours
            )
            session.add(order)
            session.commit()
    if validation_error:
        return make_resp(
            {
                'validation_error': {
                    "orders": validation_error
                }
            }, 400)
    else:
        return make_resp(
            {
                "orders": ids
            }, 201)


@app.route("/orders/assign", methods=["POST"])
def post_order_assign():
    time_now = datetime.now()
    session = db_session.create_session()
    get_data = request.json
    courier = session.query(Courier).filter(Courier.id == get_data['courier_id']).first()
    if courier:
        if not courier.working_hours or not courier.regions:
            return make_resp({"orders": []}, 200)
        max_weight = WEIGHT[courier.type]
        orders_execution = courier.orders
        uncompletable_orders = [i.order for i in orders_execution if i.complete_time == DEFAULT_COMPLETE_TIME]
        add_weight = max_weight - sum([order.weight for order in uncompletable_orders])
        time_condition = "("
        region_condition = "("
        for hour in courier.working_hours:
            time_condition += f"(dh.start <= '{hour.end}' and dh.end >= '{hour.start}') or "
        time_condition = time_condition[:-4]
        time_condition += ")"
        for reg in courier.regions:
            region_condition += f"o.region_number = {reg.region_number} or "
        region_condition = region_condition[:-4]
        region_condition += ")"
        res = session.execute("select * from orders o "
                              "join delivery_hours dh on o.id = dh.order_id  " +
                              "where o.is_taken = 0 and " + time_condition + " and " + region_condition +
                              f" and o.weight <= {WEIGHT[courier.type]} group by o.id limit {add_weight * 100}").fetchall()
        res_ids = [i[0] for i in res]
        orders = session.query(Order).filter(Order.id.in_(res_ids)).all()
        courier_orders = []
        for order in orders:
            if add_weight >= order.weight:
                add_weight -= order.weight
                courier_orders.append(order)
            elif not WEIGHT:
                break
        for order in courier_orders:
            order_execution = OrderExecution(
                order_id=order.id,
                courier_id=courier.id,
                courier_type=courier.type,
                assign_time=time_now,
                complete_time=DEFAULT_COMPLETE_TIME
            )
            order.is_taken = True
            session.add(order_execution)
            session.commit()
        orders = [i.order for i in courier.orders if i.complete_time == DEFAULT_COMPLETE_TIME]

        if orders:
            assign_time = DEFAULT_COMPLETE_TIME
            for i in courier.orders:
                if i.complete_time == DEFAULT_COMPLETE_TIME and i.assign_time > assign_time:
                    assign_time = i.assign_time
            return make_resp(
                {"orders": [{"id": i.id} for i in orders],
                 "assign_time": assign_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")}, 200)
        else:
            return make_resp({
                "orders": [{"id": i.id} for i in orders]}, 200)
    else:
        return make_resp('', 400)


@app.route("/orders/complete", methods=["POST"])
def post_orders_complete():
    session = db_session.create_session()
    get_data = request.json
    date_time = datetime.strptime(get_data['complete_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
    valid_keys = ('courier_id', 'order_id', 'complete_time')
    if not keys_is_has_dict_keys(get_data, valid_keys) or not dict_has_keys(get_data, valid_keys):
        return make_resp('', 400)
    complete_order = session.query(OrderExecution).filter(OrderExecution.courier_id == get_data['courier_id'],
                                                          OrderExecution.order_id == get_data['order_id']).first()
    if complete_order:
        complete_order.complete_time = date_time
        complete_order.set_delivery_time(session)
        complete_id = complete_order.order_id
        session.commit()
        return make_resp(
            {"order_id": complete_id}, 200)
    return make_resp('', 400)


@app.route("/couriers/<int:id>", methods=["GET"])
def get_courier_by_id(id):
    session = db_session.create_session()
    courier = session.query(Courier).filter(Courier.id == id).first()
    if courier:
        courier_type = courier.type
        regions = [i.region_number for i in courier.regions]
        working_hours = [i.working_hour for i in courier.working_hours]
        rating = courier.get_rating(session)
        earnings = courier.get_earning(session)
        return make_resp({"id": id,
                          "type": courier_type,
                          "regions": regions,
                          "working_hours": working_hours,
                          "rating": rating,
                          "earnings": earnings
                          }, 200)
    else:
        return make_resp({'Message': "Courier not found"}, 400)


def main():
    db_session.global_init("/home/aleksandr/PycharmProjects/YandexSchoolProject/data_base/delivery_data_base.sqlite")
    app.run(host='0.0.0.0', port="8080")

# For virtual machine
# serve(app, host='0.0.0.0', port="8080")
# For local machine
# app.run(host='0.0.0.0', port="8080")

main()
