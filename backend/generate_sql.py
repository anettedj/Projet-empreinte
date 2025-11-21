# Génération SQL pour DB1_B
output_file = "insert_empreintes_db1.sql"

with open(output_file, "w", encoding="utf-8") as f:
    for user_id, base_id in enumerate(range(101, 111), start=1):  # 101 à 110 -> 10 utilisateurs
        for empreinte_num in range(1, 9):  # 8 empreintes chacun
            chemin = f"C://xampp//htdocs//empreintes//backend//images//fvc//DB1_B//{base_id}_{empreinte_num}.tif"
            f.write(
                f"INSERT INTO Empreinte (utilisateur_id, image_path, doigt, minutiae_data) "
                f"VALUES ({user_id}, '{chemin}', 'doigt{empreinte_num}', NULL);\n"
            )

print(f"SQL généré dans {output_file}")
