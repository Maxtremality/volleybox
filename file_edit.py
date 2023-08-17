import os


# Функция для обновления года в формате 2016/2017
def update_year(year_str):
    years = year_str.split('/')
    if len(years) == 2:
        year1, year2 = int(years[0]), int(years[1])
        if year2 > 2024 and year2 - 100 >= year1:
            return f"{year1}/{year2 - 100}"
    return year_str


def main():
    # Открываем файл для чтения и записи
    with open('data_исходный.txt', 'r') as file:
        lines = file.readlines()

    # Создаем список списков
    list_of_lists = [line.strip().split(',') for line in lines]

    # Добавляем пустой элемент на 5-ое место в каждом внутреннем списке
    for inner_list in list_of_lists:
        years = update_year(inner_list[4])
        inner_list[4] = years
        if inner_list[2] == 'Outside Hitter':
            inner_list[2] = 'Outside Spiker'
        inner_list.insert(4, '')

    # Разбиваем на части с примерно равным количеством строк
    num_parts = 598
    chunk_size = len(list_of_lists) // num_parts

    # Рассчитываем остаток для равномерного распределения строк
    remainder = len(list_of_lists) % num_parts

    # Создаем 10 списков списков и записываем соответствующие части в каждый список
    split_lists = []
    start = 0
    for i in range(num_parts):
        if i < remainder:
            end = start + chunk_size + 1
        else:
            end = start + chunk_size
        split_lists.append(list_of_lists[start:end])
        start = end

    # Записываем каждую часть в отдельный файл
    for i, chunk in enumerate(split_lists):
        filename = os.path.join('volleybox', f'data_{i + 1}.txt')

        with open(filename, 'w') as chunk_file:
            for inner_list in chunk:
                line = ','.join(inner_list) + '\n'
                chunk_file.write(line)


if __name__ == '__main__':
    main()
