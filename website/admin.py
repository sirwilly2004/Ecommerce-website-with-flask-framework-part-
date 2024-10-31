from flask import Blueprint, render_template,flash, redirect, url_for,send_from_directory
from flask_login import login_required,current_user
from .forms import ShopItemsForm,OrderForm
from werkzeug.utils import secure_filename
from .models import Product, Order,Customer
from . import db

admin = Blueprint('admin', __name__)


@admin.route('/media/<path:filename>')
def get_image(filename):
    return send_from_directory('../media', filename)

@admin.route('/add-shop-items', methods=['GET', 'POST'])
@login_required
def add_shop_item():
    if current_user.id == 1:
        form = ShopItemsForm()
        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data
            file = form.product_picture.data

            if file:
                file_name = secure_filename(file.filename)
                file_path = f'./media/{file_name}'
                file.save(file_path)
                new_shop_item = Product(
                    product_name=product_name, current_price=current_price, previous_price=previous_price, 
                    in_stock=in_stock, flash_sale=flash_sale, product_picture=file_path)
                try:
                    db.session.add(new_shop_item)
                    db.session.commit()
                    flash(f'{product_name} Item added successfully!', 'success')
                    return redirect(url_for('admin.shop_items')) 
                except Exception as e:
                    print(e)
                    flash('Product Not Added!!')

        return render_template('add-shop-items.html', form=form)

    return render_template('404.html') 

@admin.route('/shop-items', methods=['GET', 'POST'])
@login_required
def shop_items():
    if current_user.id == 1:
        items = Product.query.order_by(Product.date_added).all()
        return render_template('shop_items.html', items=items)
    return render_template('404.html')


@admin.route('/update-item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def update_item(item_id):
    if current_user.id == 1:
        form = ShopItemsForm()
        item_to_update = Product.query.get(item_id)
        # Set placeholders for existing values of the items in the database 
        form.product_name.render_kw = {'placeholder': item_to_update.product_name}
        form.previous_price.render_kw = {'placeholder': item_to_update.previous_price}
        form.current_price.render_kw = {'placeholder': item_to_update.current_price}
        form.in_stock.render_kw = {'placeholder': item_to_update.in_stock}
        form.flash_sale.render_kw = {'placeholder': item_to_update.flash_sale}

        if form.validate_on_submit():
            product_name = form.product_name.data
            current_price = form.current_price.data
            previous_price = form.previous_price.data
            in_stock = form.in_stock.data
            flash_sale = form.flash_sale.data

            # Check if a new file has been uploaded
            file = form.product_picture.data
            if file:
                file_name = secure_filename(file.filename)
                file_path = f'./media/{file_name}'
                file.save(file_path)
                product_picture = file_path
            else:
                product_picture = item_to_update.product_picture  # Keep the existing picture
            try:
                Product.query.filter_by(id=item_id).update(dict(
                    product_name=product_name,
                    current_price=current_price,
                    previous_price=previous_price,
                    in_stock=in_stock,
                    flash_sale=flash_sale,
                    product_picture=product_picture  # Use the updated or existing picture
                ))

                db.session.commit()
                flash(f'{product_name} updated successfully')
                print('Product Updated')
                return redirect(url_for('admin.shop_items'))
            except Exception as e:
                print('Product not updated', e)
                flash('Item Not Updated!!!')
        return render_template('update_item.html', form=form, item=item_to_update)
    return render_template('404.html')

@admin.route('/delete-item/<int:item_id>', methods=['POST', 'GET'])
@login_required
def delete_item(item_id):
    if current_user.id == 1:
        item_to_delete = Product.query.get(item_id)
        try:
            db.session.delete(item_to_delete)
            db.session.commit()
            flash(f'Item {item_to_delete.product_name} deleted successfully')
            print('Item Deleted')
            return redirect(url_for('admin.shop_items'))
        except Exception as e:
            print('Item not deleted', e)
            flash('Item Not Deleted!!!')
            return redirect(url_for('admin.shop-items'))
    return render_template('404.html')


@admin.route('/view-orders')
@login_required
def order_view():
    if current_user.id == 1:
        orders = Order.query.all()
        return render_template('view_orders.html', orders=orders)
    return render_template('404.html')


@admin.route('/update-order/<int:order_id>', methods=['GET', 'POST'])
@login_required
def update_order(order_id):
    if current_user.id == 1:
        form = OrderForm()

        order = Order.query.get(order_id)

        if form.validate_on_submit():
            status = form.order_status.data
            order.status = status

            try:
                db.session.commit()
                flash(f'Order {order_id} Updated successfully')
                return redirect('/view-orders')
            except Exception as e:
                print(e)
                flash(f'Order {order_id} not updated')
                return redirect('/view-orders')

        return render_template('order_updates.html', form=form)

    return render_template('404.html')


@admin.route('/customers')
@login_required
def display_customers():
    if current_user.id == 1:
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)
    return render_template('404.html')


@admin.route('/admin-page')
@login_required
def admin_page():
    if current_user.id == 1:
        return render_template('admin.html')
    return render_template('404.html')