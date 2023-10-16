import requests

response = requests.get('https://docs.microsoft.com/api/learn/catalog/')

data = response.json()
courses_data = data['courses']
print(len(courses_data))

final_data = 'course_code|course_number|course_name|course_type|training_type|description|duration|access_url|roles;products|study_guide'
for course in courses_data:
    try:
        course_code = course['uid']
        course_number = str(course['course_number']).replace("\n", "")
        course_name = str(course['title']).replace("\n", "")
        training_type = str(course['levels']).replace("\n", "")
        course_type = str(course['type']).replace("\n", "")
        description = str(course['summary']).replace("\n", "")
        duration = str(course['duration_in_hours']).replace("\n", "")
        access_url = str(course['url']).replace("\n", "")
        roles = str(course['roles']).replace("\n", "")
        products = str(course['products']).replace("\n", "")
        study_guide = str(course['study_guide']).replace("\n", "")

        final_data += f'\n{course_code}|' \
                      f'{course_number}|' \
                      f'{course_name}|' \
                      f'{course_type}|' \
                      f'{training_type}|' \
                      f'{description}|' \
                      f'{duration}|' \
                      f'{access_url}|' \
                      f'{roles}|' \
                      f'{products}|' \
                      f'{study_guide}' \
                      f''

        # print(f"course_code : {course_code}")
        # print(f"course_name : {course_name}")
        # print(f"duration : {duration}")
        # print(f"access_url : {access_url}")
        # print(f"study_guide : {study_guide}")
    except:
        print(course)


with open("/Users/chanduarepalli/Documents/microsoft_data.csv", 'w') as file:
    file.write(final_data)
    file.close()