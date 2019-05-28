from django import template

register = template.Library()

@register.filter(name='get_type')
def get_type(value):
    return str(type(value))

# @register.filter(name='get_elements')
# def get_elements(value, n):
#     result = dict()
#     for i in range(int(n)):
#         k, v = next(iter(value.items()))
#         result[k] = v
#     return result

@register.simple_tag
def get_elements(value, n):
    # value là dictionary chứa tất cả title và url mà mình đưa vào
    # n là số bộ kết quả cần lấy (n=5 sẽ lấy n bộ kết quả ra)
    # Tạo 1 dictionary tên result để chứa kết quả (chỉ nên chứa n bộ title + url)
    result = dict()
    # Tạo 1 dictionary tạm thời (temporary) là bản copy của value
    # Cần phải tạo 1 bản copy và làm việc trên bản copy để khỏi hư bản chính (là value)
    tmp = dict(value)
    # Cho i chạy trong n lần

    for i in range(int(n)):
     try:
        # Lấy title, url từ bản copy
        title, url = tmp.popitem()
        # Đưa vào trong result
        result[title] = url

    # Trả về kết quả cuối cùng là result
     except KeyError:
         continue
    return result
# @register.simple_tag
# def get_elements2(value, n):
#     # value là dictionary chứa tất cả title và url mà mình đưa vào
#     # n là số bộ kết quả cần lấy (n=5 sẽ lấy 5 bộ kết quả ra)
#     # Tạo 1 dictionary tên result để chứa kết quả (chỉ nên chứa 5 bộ title + url)
#     result = dict()
#     # Tạo 1 dictionary tạm thời (temporary) là bản copy của value
#     # Cần phải tạo 1 bản copy và làm việc trên bản copy để khỏi hư bản chính (là value)
#     tmp = dict(value)
#     # Cho i chạy trong n lần

#     for i in range(int(n)):
#      try:
#         # Lấy title, img từ bản copy
#         title, img = tmp.popitem()
#         # Đưa vào trong result
#         result[title] = img

#     # Trả về kết quả cuối cùng là result
#      except KeyError:
#          continue
#     return result
# @register.simple_tag
# def get_elements3(value, n):
#     # value là dictionary chứa tất cả title và url mà mình đưa vào
#     # n là số bộ kết quả cần lấy (n=5 sẽ lấy 5 bộ kết quả ra)
#     # Tạo 1 dictionary tên result để chứa kết quả (chỉ nên chứa 5 bộ title + date)
#     result = dict()
#     # Tạo 1 dictionary tạm thời (temporary) là bản copy của value
#     # Cần phải tạo 1 bản copy và làm việc trên bản copy để khỏi hư bản chính (là value)
#     tmp = dict(value)
#     # Cho i chạy trong n lần

#     for i in range(int(n)):
#      try:
#         # Lấy title, date từ bản copy
#         title, date = tmp.popitem()
#         # Đưa vào trong result
#         result[title] = date

#     # Trả về kết quả cuối cùng là result
#      except KeyError:
#          continue
#     return result
# # @register.simple_tag
# # def get_Movies(value , n)


@register.simple_tag
def get_elements4(value, year_selected_list, n):
    tmp = dict(value)
    # Kiểu như là sẽ tạo 1 biến selected để chứa kết quả sau khi đã lọc
    # Khi  đưa input vô thì nó là 1 dictionary bao gồm tất cả (chưa lọc gì hết),  tạo 1 biến selected để chứa kết quả
    selected = dict()
    # Chạy vòng for, tạo 2 biến tạm là key và val để chứa giá trị có trong tmp
    #  đó là lý do  chạy dòng code dưới 
    for movie_name, url in tmp.items():
        # Ở đây  xem key coi thử nó có nằm trong danh sách film cần lấy ko?
        # key ở đây chính là tên film, year_selected_list là danh sách tên film mình đã lọc theo năm
        if movie_name in year_selected_list:
            # Nếu có trong danh sách thì mình lấy đưa nó vào selected
            selected[movie_name] = url
    # Cuối cùng là lấy film từ selected (đã được lọc) thay vì lấy tất cả các film
    if len(tmp) > int(n):
        return get_elements(selected, int(n))
    else:
        return get_elements(selected, len(tmp))


@register.simple_tag
def get_date_filter(value, opr, year_cut):
    result = list()
    tmp = dict(value)
    if len(tmp) < 10:
        return tmp
    for key, val in tmp.items():
        if opr == ">=":
            if int(val) >= int(year_cut):
                result.append(key)
        elif opr == "<=":
            if int(val) <= int(year_cut):
                result.append(key)
        elif opr == "==":
            if int(val) == int(year_cut):
                result.append(key)
        elif opr == ">":
            if int(val) > int(year_cut):
                result.append(key)
        elif opr == "<":
            if int(val) < int(year_cut):
                result.append(key)
    return result