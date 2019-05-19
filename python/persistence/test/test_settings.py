from persistence.settings import SettingsNode, SelectWidget, OptionWidget, TextWidget


root = SettingsNode('root')

# # Input Devices
input_device = SettingsNode('controller', widget=SelectWidget)
root.add_child(input_device)

# Keyboard
input_device_keyboard = SettingsNode('keyboard', is_choice=True, widget=OptionWidget)
input_device_keyboard.add_child(SettingsNode('autopilot_button', widget=TextWidget))
input_device.add_child(input_device_keyboard)

# Gamepad
input_device_gamepad = SettingsNode('gamepad', is_choice=True, widget=OptionWidget)
input_device_gamepad.add_child(SettingsNode('device_id', widget=TextWidget))
input_device_gamepad.add_child(SettingsNode('autopilot_button', widget=TextWidget))
input_device_gamepad.add_child(SettingsNode('steering_axis', widget=TextWidget))
input_device.add_child(input_device_gamepad)

# # ROI
roi = SettingsNode('roi')
roi.add_child(SettingsNode('x1', value='547', widget=TextWidget))
roi.add_child(SettingsNode('x2', widget=TextWidget))
roi_y1 = SettingsNode('y1', widget=TextWidget)
roi.add_child(roi_y1)
roi.add_child(SettingsNode('y2', value='750', widget=TextWidget))
root.add_child(roi)


assert root.get_node_in_tree('root.roi.y1') == roi_y1
assert root.get_value_of_child('root.roi.y2') == '750'
root.set_value_of_child('root.roi.x1', '123')
assert root.get_value_of_child('root.roi.x1') == '123'

flat_tree = root.get_flat_sub_tree()
root.fill_tree_flat({'root.roi.y2': '100'})
assert root.get_value_of_child('root.roi.y2') == '100'
root.fill_tree_flat(flat_tree)
assert root.get_value_of_child('root.roi.y2') == '750'


print(root.get_flat_sub_tree())
print(input_device.render_element())
print(str(root.get_node_in_tree('roi.x2')))
