stat = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        GROUP BY name"""

today = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        WHERE DATE(date) = CURDATE() 
        GROUP BY name"""

insert = """INSERT INTO reports (`id`, `name`, `date`, `level`, `link`, `description`) 
        VALUES (%s, %s, %s, %s, %s, %s)"""
