update fg_sale_order set sync = TRUE;
update fg_sale_order_line set sync = TRUE;
UPDATE fg_sale_order_line SET aux_qty = ( aux_qty/ product_uom_qty) * "ceil" (product_uom_qty / 3) where product_uom_qty>0;
UPDATE fg_sale_order_line SET product_uom_qty = "ceil" (product_uom_qty / 3) where product_uom_qty>0;
UPDATE fg_sale_order_line SET subtotal_amount = aux_qty * unit_price;
