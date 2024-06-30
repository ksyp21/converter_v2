from tkinter import *
import customtkinter
import json
import yaml
import os
from tkinter import messagebox
from tkinter import filedialog

# Set theme and color options
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

root = customtkinter.CTk()
root.title('File Converter')
initial_width = 650
initial_height = 820
root.geometry(f'{initial_width}x{initial_height}')
root.resizable(False, False)  # Disable resizing (disables maximize button)

section_frames=[]

def save_workflows_to_yaml():
    
        workflows = []
        for section in section_frames:
            workflow = {}
            
            # Get the workflow type
            field_frame = section.winfo_children()[1]
            workflow_type = field_frame.grid_slaves(row=0, column=1)[0].get().strip()
            workflow['workflow_type'] = workflow_type
            
            # Collect basic fields
            for i in range(1, field_frame.grid_size()[1]):
                label = field_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
                entry = field_frame.grid_slaves(row=i, column=1)[0]
                value = entry.get().strip()
                if value:  # Only add non-empty fields
                    workflow[label] = value
            
            if workflow_type in ['sync', 'async']:
                # Collect file parameters
                file_parameters = {}
                file_parameter_subitem_frame = section.winfo_children()[3]
                for i in range(file_parameter_subitem_frame.grid_size()[1]):
                    label = file_parameter_subitem_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
                    entry = file_parameter_subitem_frame.grid_slaves(row=i, column=1)[0]
                    value = entry.get().strip()
                    if value:
                        if label == "minimum_file_size_in_bytes":
                            file_parameters[label] = int(value)
                        elif label == "move_to_error_for_invalid_file":
                            file_parameters[label] = value.lower() == 'true'
                        else:
                            file_parameters[label] = value
                if file_parameters:
                    workflow['file_parameters'] = file_parameters
                
                # Collect location parameters
                location = {}
                location_subitem_frame = section.winfo_children()[5]
                for i in range(location_subitem_frame.grid_size()[1]):
                    label = location_subitem_frame.grid_slaves(row=i, column=0)[0].cget("text").strip(":")
                    entry = location_subitem_frame.grid_slaves(row=i, column=1)[0]
                    value = entry.get().strip()
                    if value:
                        location[label] = value
                if location:
                    workflow['location'] = location
            
            elif workflow_type == 'download':
                # Collect download locations
                locations = []
                location_download_subarray = section.winfo_children()[3]
                for i in range(0, location_download_subarray.grid_size()[1], 2):
                    s3_path = location_download_subarray.grid_slaves(row=i, column=1)[0].get().strip()
                    output_location = location_download_subarray.grid_slaves(row=i+1, column=1)[0].get().strip()
                    if s3_path and output_location:
                        locations.append({
                            's3_path': s3_path,
                            'output_location': output_location
                        })
                if locations:
                    workflow['location'] = locations
            
            elif workflow_type == 'cleanup':
                # Collect cleanup locations
                cleanup_locations = []
                cleanup_subarray = section.winfo_children()[3]
                for i in range(cleanup_subarray.grid_size()[1]):
                    path = cleanup_subarray.grid_slaves(row=i, column=1)[0].get().strip()
                    if path:
                        cleanup_locations.append(path)
                if cleanup_locations:
                    workflow['cleanup_location'] = cleanup_locations
            
            workflows.append(workflow)
        
        # Create a single workflows_data dictionary with all workflows
        workflows_data = {"workflows": workflows}
        
        # Convert Python object to YAML
        yaml_data = yaml.dump(workflows_data, default_flow_style=False, sort_keys=False)
        
        # Remove quotes from the YAML output
        yaml_data = yaml.dump(yaml.safe_load(yaml_data), default_flow_style=False, sort_keys=False, default_style='')
        
        # Get the user's home directory
        home_dir = os.path.expanduser("~")
        
        # Create a default file name
        file_name = "workflows.yaml"
        
        # Full path for the file
        file_path = os.path.join(home_dir, "Downloads", file_name)
        
        # Ensure the file name is unique
        counter = 1
        while os.path.exists(file_path):
            file_name = f"workflows_{counter}.yaml"
            file_path = os.path.join(home_dir, "Downloads", file_name)
            counter += 1
        
        # Write YAML data to file
        with open(file_path, "w") as file:
            file.write(yaml_data)
        
        messagebox.showinfo("Save Successful", f"YAML file saved as: {file_path}")

# main Frame
content_frame = customtkinter.CTkFrame(root)
content_frame.pack(padx=10, pady=10, fill='both', expand=True)

# Create a frame to hold the horizontally aligned widgets at the top
horizontal_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B")
horizontal_frame.pack(pady=40, fill='x', padx=10)




# Add widgets to the horizontal frame
my_label = customtkinter.CTkLabel(horizontal_frame, text="Workflow type:", font=("Helvetica", 18))
my_label.pack(side='left', padx=10)

# Add New combobox
addnew_combobox = customtkinter.CTkComboBox(horizontal_frame, values=["sync","async","download","cleanup"])
addnew_combobox.pack(side='left', padx=5 )



addnew_btn = customtkinter.CTkButton(horizontal_frame, text="Add New",width=50, command=lambda: toggle_workflow_type())
addnew_btn.pack(side='left', padx=5)

# Add edit button 
edit_btn = customtkinter.CTkButton(horizontal_frame, text="Edit",width=50)
edit_btn.pack(side='left', padx=5)

save_btn = customtkinter.CTkButton(horizontal_frame, text="Save", width=50, command=save_workflows_to_yaml)
save_btn.pack(side='left', padx=10)

# Options for combobox
my_combo = customtkinter.CTkComboBox(horizontal_frame, values=["0"])
my_combo.pack(side='left', padx=5)



def remove_form(section_frame):
    
        section_frames.remove(section_frame)
        section_frame.destroy()
        
        # Update combobox values
        update_combo_values()
        
        # Set to the first available item or empty string
        combo_values = my_combo.cget("values")
        my_combo.set(combo_values[0] if combo_values else "")
        
        # Toggle visibility to show the new current section
        toggle_section_visibility()
        
# Function to toggle visibility of section frames
def toggle_section_visibility(event=None):
    selected_item = my_combo.get()
    if not selected_item:
        return
    selected_index = int(selected_item.split(':')[0])
    for i, frame in enumerate(section_frames):
        if i == selected_index:
            frame.pack(pady=10, padx=20, anchor='w', fill='x')
        else:
            frame.pack_forget()       
        
        
def update_combo_values():
    names = []
    for i, frame in enumerate(section_frames):
        try:
            name_entry = frame.winfo_children()[1].grid_slaves(row=1, column=1)[0]
            name = name_entry.get()
        except (IndexError, AttributeError):
            name = ""
        names.append(f"{i}: {name}" if name else f"{i}")
    my_combo.configure(values=names if names else [""])
    
# workflow_type: sync
def create_sync_workflow():
    # Create a frame for the entire section
    section_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B", border_width=2)
    
    section_frames.append(section_frame)
    update_combo_values()
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")
    toggle_section_visibility()
    # Add internal padding to the section frame (inside padding)
    section_frame.pack_configure(ipadx=10, ipady=20)
    
    # Create frame for workflow_type label and combobox
    cross_button_frame = customtkinter.CTkFrame(section_frame)
    cross_button_frame.pack(pady=10, padx=30, anchor='w', fill='x')

    cross_btn = customtkinter.CTkButton(cross_button_frame, text="X", width=40, fg_color="red", hover_color="maroon", command=lambda: remove_form(section_frame))
    cross_btn.pack(side='right', padx=30)
    
    # Create a frame for the label-entry pairs
    field_frame = customtkinter.CTkFrame(section_frame)
    field_frame.pack(padx=50, anchor='w', fill='x')

    location_downloads = customtkinter.CTkFrame(section_frame)
    location_downloads.pack(padx=50, anchor='w', fill='x')

    file_parameter_subitem_frame = customtkinter.CTkFrame(section_frame)
    file_parameter_subitem_frame.pack(padx=70, anchor='w', fill='x')

    location_label_frame = customtkinter.CTkFrame(section_frame)
    location_label_frame.pack(padx=50, anchor='w', fill='x')

    location_subitem_frame = customtkinter.CTkFrame(section_frame)
    location_subitem_frame.pack(padx=70, anchor='w', fill='x')

    # Define the label-entry pairs including nested structure
    fields = [
        ("workflow_type:", None),
        ("name:", None),
        ("cron:", None),
        ("workflow_id:", None)
    ]

    file_parameter_label = customtkinter.CTkLabel(location_downloads, text="file_parameters:", font=("Helvetica", 18))
    file_parameter_label.pack(side='left')

    file_parameter_subitem_entrypair = [
        ("input_file_type:", None),
        ("output_file_type", None)
    ]

    location_label = customtkinter.CTkLabel(location_label_frame, text="location:", font=("Helvetica", 18))
    location_label.pack(side='left')

    location_subitem_entrypair = [
        ("queue:", None),
        ("output:", None),
        ("archive:", None),
        ("error:", None)
    ]

    # Add label-entry pairs to the frame using grid layout for fields
    fields_row_index = 0
    for i, (label_text, content) in enumerate(fields):
        label = customtkinter.CTkLabel(field_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=fields_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(field_frame)
        else:
            entry = customtkinter.CTkComboBox(field_frame, values=content)
            if label_text == "workflow_type:":
                workflow_type_combobox = entry

        entry.grid(row=fields_row_index, column=1, padx=10, pady=5, sticky='ew')

        if label_text == "workflow_id:":
            workflow_id_label = label

        fields_row_index += 1

    # Add label-entry pairs to file_parameter_subitems_frame 
    file_parameter_subitem_row_index = 0
    for i, (label_text, content) in enumerate(file_parameter_subitem_entrypair):
        label = customtkinter.CTkLabel(file_parameter_subitem_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=file_parameter_subitem_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(file_parameter_subitem_frame)
        else:
            entry = customtkinter.CTkComboBox(file_parameter_subitem_frame, values=content)
            entry.set("False")
        entry.grid(row=file_parameter_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
        
        
        file_parameter_subitem_row_index += 1
        
        location_subitem_row_index = 0
        for i, (label_text, content) in enumerate(location_subitem_entrypair):
            label = customtkinter.CTkLabel(location_subitem_frame, text=label_text, font=("Helvetica", 18))
            label.grid(row=location_subitem_row_index, column=0, pady=5, sticky='w')

            if content is None:
                entry = customtkinter.CTkEntry(location_subitem_frame)

            entry.grid(row=location_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
            location_subitem_row_index += 1

    # Ensure the columns expand to fill the available space
    field_frame.grid_columnconfigure(1, weight=1)
    file_parameter_subitem_frame.grid_columnconfigure(1, weight=1)
    location_subitem_frame.grid_columnconfigure(1, weight=1)

    # Set initial border colors for required fields
    field_frame.grid_slaves(row=0,column=1)[0].insert(0,"sync")
    field_frame.grid_slaves(row=1, column=1)[0].configure(placeholder_text="*required")  # name
    field_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # cron
    field_frame.grid_slaves(row=3, column=1)[0].configure(placeholder_text="*required")  # workflow_id / s3_path
    file_parameter_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # input_file_type
    location_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # queue
    location_subitem_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # archive
    location_subitem_frame.grid_slaves(row=3, column=1)[0].configure(placeholder_text="*required")  # error
    
    # Bind the name entry to update combo values when it changes
    name_entry = field_frame.grid_slaves(row=1, column=1)[0]
    name_entry.bind("<KeyRelease>", lambda e: update_combo_values())
    
    


# Worklfow_type: async
def create_async_workflow():
    # Create a frame for the entire section
    section_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B", border_width=2)
    
    section_frames.append(section_frame)
    update_combo_values()
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")
    toggle_section_visibility()
    
    # Add internal padding to the section frame (inside padding)
    section_frame.pack_configure(ipadx=10, ipady=20)

    # Create frame for workflow_type label and combobox
    cross_button_frame = customtkinter.CTkFrame(section_frame)
    cross_button_frame.pack(pady=10, padx=30, anchor='w', fill='x')

    cross_btn = customtkinter.CTkButton(cross_button_frame, text="X", width=40, fg_color="red", hover_color="maroon", command=lambda: remove_form(section_frame))
    cross_btn.pack(side='right',padx=30)

    # Create a frame for the label-entry pairs
    field_frame = customtkinter.CTkFrame(section_frame)
    field_frame.pack(padx=50, anchor='w', fill='x')

    location_downloads = customtkinter.CTkFrame(section_frame)
    location_downloads.pack(padx=50, anchor='w', fill='x')

    file_parameter_subitem_frame = customtkinter.CTkFrame(section_frame)
    file_parameter_subitem_frame.pack(padx=70, anchor='w', fill='x')

    location_label_frame = customtkinter.CTkFrame(section_frame)
    location_label_frame.pack(padx=50, anchor='w', fill='x')

    location_subitem_frame = customtkinter.CTkFrame(section_frame)
    location_subitem_frame.pack(padx=70, anchor='w', fill='x')

    # Define the label-entry pairs including nested structure
    fields = [
        ("workflow_type:", None),
        ("name:", None),
        ("cron:", None),
        ("s3_path:", None)
    ]

    file_parameter_label = customtkinter.CTkLabel(location_downloads, text="file_parameters:", font=("Helvetica", 18))
    file_parameter_label.pack(side='left')

    file_parameter_subitem_entrypair = [
        ("input_file_type:", None),
        ("output_file_type", None),
        ("target_filename:", None),
        ("minimum_file_size_in_bytes:", None),
        ("move_to_error_for_invalid_file:", ["True","False"])
    ]

    location_label = customtkinter.CTkLabel(location_label_frame, text="location:", font=("Helvetica", 18))
    location_label.pack(side='left')

    location_subitem_entrypair = [
        ("queue:", None),
        ("archive:", None),
        ("error:", None)
    ]

    # Add label-entry pairs to the frame using grid layout for fields
    fields_row_index = 0
    for i, (label_text, content) in enumerate(fields):
        label = customtkinter.CTkLabel(field_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=fields_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(field_frame)
        else:
            entry = customtkinter.CTkComboBox(field_frame, values=content)
            if label_text == "workflow_type:":
                workflow_type_combobox = entry

        entry.grid(row=fields_row_index, column=1, padx=10, pady=5, sticky='ew')

        if label_text == "workflow_id:":
            workflow_id_label = label

        fields_row_index += 1

    # Add label-entry pairs to file_parameter_subitems_frame 
    file_parameter_subitem_row_index = 0
    for i, (label_text, content) in enumerate(file_parameter_subitem_entrypair):
        label = customtkinter.CTkLabel(file_parameter_subitem_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=file_parameter_subitem_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(file_parameter_subitem_frame)
        else:
            entry = customtkinter.CTkComboBox(file_parameter_subitem_frame, values=content)
            entry.set("False")
        entry.grid(row=file_parameter_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
        
        
        file_parameter_subitem_row_index += 1
        
        location_subitem_row_index = 0
        for i, (label_text, content) in enumerate(location_subitem_entrypair):
            label = customtkinter.CTkLabel(location_subitem_frame, text=label_text, font=("Helvetica", 18))
            label.grid(row=location_subitem_row_index, column=0, pady=5, sticky='w')

            if content is None:
                entry = customtkinter.CTkEntry(location_subitem_frame)

            entry.grid(row=location_subitem_row_index, column=1, padx=10, pady=5, sticky='ew')
            location_subitem_row_index += 1

    # Ensure the columns expand to fill the available space
    field_frame.grid_columnconfigure(1, weight=1)
    file_parameter_subitem_frame.grid_columnconfigure(1, weight=1)
    location_subitem_frame.grid_columnconfigure(1, weight=1)

    # Set initial border colors for required fields
    field_frame.grid_slaves(row=0,column=1)[0].insert(0,"async")
    field_frame.grid_slaves(row=1, column=1)[0].configure(placeholder_text="*required")  # name
    field_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # cron
    field_frame.grid_slaves(row=3, column=1)[0].configure(placeholder_text="*required")  # workflow_id / s3_path
    file_parameter_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # input_file_type
    location_subitem_frame.grid_slaves(row=0, column=1)[0].configure(placeholder_text="*required")  # queue
    location_subitem_frame.grid_slaves(row=1, column=1)[0].configure(placeholder_text="*required")  # archive
    location_subitem_frame.grid_slaves(row=2, column=1)[0].configure(placeholder_text="*required")  # error
    
    ## Bind the name entry to update combo values when it changes
    name_entry = field_frame.grid_slaves(row=1, column=1)[0]
    name_entry.bind("<KeyRelease>", lambda e: update_combo_values())
    

    
# Worklfow_type: download
def create_download_workflow():
    # Create a frame for the entire section
    section_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B", border_width=2)
    
    section_frames.append(section_frame)
    update_combo_values()
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")
    toggle_section_visibility()
    
    # Add internal padding to the section frame (inside padding)
    section_frame.pack_configure(ipadx=10, ipady=20)

    # Create frame for workflow_type label and combobox
    cross_button_frame = customtkinter.CTkFrame(section_frame)
    cross_button_frame.pack(pady=10, padx=30, anchor='w', fill='x')

    cross_btn = customtkinter.CTkButton(cross_button_frame, text="X", width=40, fg_color="red", hover_color="maroon", command=lambda: remove_form(section_frame))
    cross_btn.pack(side='right', padx=30)

    # Create a frame for the label-entry pairs
    field_frame = customtkinter.CTkFrame(section_frame)
    field_frame.pack(padx=50, anchor='w', fill='x')

    location_downloads = customtkinter.CTkFrame(section_frame)
    location_downloads.pack(padx=50, anchor='w', fill='x')

    global location_download_subarray
    location_download_subarray = customtkinter.CTkFrame(section_frame)
    location_download_subarray.pack(padx=70, anchor='w', fill='x')

    # Define the label-entry pairs including nested structure
    fields = [
        ("workflow_type:", None),
        ("name:", None),
        ("cron:", None)
    ]

    file_parameter_label = customtkinter.CTkLabel(location_downloads, text="location:", font=("Helvetica", 18))
    file_parameter_label.pack(side='left')
    plus_button_button = customtkinter.CTkButton(location_downloads, text="+", command=add_download_location)
    plus_button_button.pack(side='right')

    # Add label-entry pairs to the frame using grid layout for fields
    fields_row_index = 0
    for i, (label_text, content) in enumerate(fields):
        label = customtkinter.CTkLabel(field_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=fields_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(field_frame)
        else:
            entry = customtkinter.CTkComboBox(field_frame, values=content)
            if label_text == "workflow_type:":
                workflow_type_combobox = entry

        entry.grid(row=fields_row_index, column=1, padx=10, pady=5, sticky='ew')

        fields_row_index += 1

    add_download_location()  # Add the initial pair of entries

    # Ensure the columns expand to fill the available space
    field_frame.grid_columnconfigure(1, weight=1)
    location_download_subarray.grid_columnconfigure(1, weight=1)
  
    # Set initial border colors for required fields
    field_frame.grid_slaves(row=0, column=1)[0].insert(0, "download")
    
    # Bind the name entry to update combo values when it changes
    name_entry = field_frame.grid_slaves(row=1, column=1)[0]
    name_entry.bind("<KeyRelease>", lambda e: update_combo_values())
    
def add_download_location():
    row = location_download_subarray.grid_size()[1]  # Get the current number of rows
    
    s3_path_label = customtkinter.CTkLabel(location_download_subarray, text="- s3_path:", font=("Helvetica", 18))
    s3_path_label.grid(row=row, column=0, pady=5, sticky='w')
    s3_path_entry = customtkinter.CTkEntry(location_download_subarray)
    s3_path_entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')

    output_location_label = customtkinter.CTkLabel(location_download_subarray, text="output_location:", font=("Helvetica", 18))
    output_location_label.grid(row=row+1, column=0, pady=5, sticky='w')
    output_location_entry = customtkinter.CTkEntry(location_download_subarray)
    output_location_entry.grid(row=row+1, column=1, padx=10, pady=5, sticky='ew')

    location_download_subarray.grid_columnconfigure(1, weight=1)

# Worklfow_type: cleanup
def create_cleanup_workflow():
    # Create a frame for the entire section
    section_frame = customtkinter.CTkFrame(content_frame, fg_color="#2B2B2B", border_width=2)
    
    section_frames.append(section_frame)
    update_combo_values()
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")
    toggle_section_visibility()
    
    # Add internal padding to the section frame (inside padding)
    section_frame.pack_configure(ipadx=10, ipady=20)

    # Create frame for workflow_type label and combobox
    cross_button_frame = customtkinter.CTkFrame(section_frame)
    cross_button_frame.pack(pady=10, padx=30, anchor='w', fill='x')

    cross_btn = customtkinter.CTkButton(cross_button_frame, text="X", width=40, fg_color="red", hover_color="maroon", command=lambda: remove_form(section_frame))
    cross_btn.pack(side='right', padx=30)

    # Create a frame for the label-entry pairs
    field_frame = customtkinter.CTkFrame(section_frame)
    field_frame.pack(padx=50, anchor='w', fill='x')

    cleanup_location = customtkinter.CTkFrame(section_frame)
    cleanup_location.pack(padx=50, anchor='w', fill='x')

    global cleanup_subarray
    cleanup_subarray = customtkinter.CTkFrame(section_frame)
    cleanup_subarray.pack(padx=70, anchor='w', fill='x')

    # Define the label-entry pairs including nested structure
    fields = [
        ("workflow_type:", None),
        ("name:", None),
        ("cleanup_days:", None)
    ]

    file_parameter_label = customtkinter.CTkLabel(cleanup_location, text="cleanup_location:", font=("Helvetica", 18))
    file_parameter_label.pack(side='left')
    plus_button_button = customtkinter.CTkButton(cleanup_location, text="+", command=add_cleanup_location)
    plus_button_button.pack(side='right')

    # Add label-entry pairs to the frame using grid layout for fields
    fields_row_index = 0
    for i, (label_text, content) in enumerate(fields):
        label = customtkinter.CTkLabel(field_frame, text=label_text, font=("Helvetica", 18))
        label.grid(row=fields_row_index, column=0, pady=5, sticky='w')

        if content is None:
            entry = customtkinter.CTkEntry(field_frame)
        else:
            entry = customtkinter.CTkComboBox(field_frame, values=content)
            if label_text == "workflow_type:":
                workflow_type_combobox = entry

        entry.grid(row=fields_row_index, column=1, padx=10, pady=5, sticky='ew')

        fields_row_index += 1

    add_cleanup_location()  # Add the initial cleanup location entry

    # Ensure the columns expand to fill the available space
    field_frame.grid_columnconfigure(1, weight=1)
    cleanup_subarray.grid_columnconfigure(1, weight=1)

    # Set initial border colors for required fields
    field_frame.grid_slaves(row=0,column=1)[0].insert(0,"cleanup")
    
    # Bind the name entry to update combo values when it changes
    name_entry = field_frame.grid_slaves(row=1, column=1)[0]
    name_entry.bind("<KeyRelease>", lambda e: update_combo_values())
    
def add_cleanup_location():
    row = cleanup_subarray.grid_size()[1]  # Get the current number of rows
    
    path_label = customtkinter.CTkLabel(cleanup_subarray, text="- path:", font=("Helvetica", 18))
    path_label.grid(row=row, column=0, pady=5, sticky='w')
    path_entry = customtkinter.CTkEntry(cleanup_subarray)
    path_entry.grid(row=row, column=1, padx=10, pady=5, sticky='ew')

    cleanup_subarray.grid_columnconfigure(1, weight=1)

def toggle_workflow_type(event=None):
    selected_item = addnew_combobox.get()
    if selected_item == "sync":
        create_sync_workflow()
    elif selected_item == "async":
        create_async_workflow()
    elif selected_item == "download":
        create_download_workflow()
    else:
        create_cleanup_workflow()
    
    # Update combo values and set to the newly created workflow
    update_combo_values()
    combo_values = my_combo.cget("values")
    my_combo.set(combo_values[-1] if combo_values else "")
    toggle_section_visibility()


    
# Bind the toggle_section_visibility function to the combobox
my_combo.configure(command=toggle_section_visibility)
    
#addnew_combobox.configure(command=toggle_workflow_type)


root.mainloop()