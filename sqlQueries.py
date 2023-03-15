stat = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        GROUP BY name;"""

today = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        WHERE DATE(date) = CURDATE() 
        GROUP BY name;"""

yesterday = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        WHERE DATE(date) = DATE_SUB(CURDATE(), INTERVAL 1 DAY)
        GROUP BY name;"""

week = """SELECT name, 
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "easy" GROUP BY id), 0) AS easy,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "medium" GROUP BY id), 0) AS medium,
        IFNULL((SELECT COUNT(id) FROM tgChallengeBot.reports AS t2 WHERE t1.name = t2.name AND level like "hard" GROUP BY id), 0) AS hard
        FROM tgChallengeBot.reports AS t1
        WHERE DATE(date) BETWEEN DATE_SUB(NOW(), INTERVAL 1 WEEK) AND NOW()
        GROUP BY name;"""

insert = """INSERT INTO reports (`id`, `name`, `date`, `level`, `link`, `description`) 
        VALUES (%s, %s, %s, %s, %s, %s);"""
