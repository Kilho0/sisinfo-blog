-- Consultas da parte 4, executadas sobre o db.sqlite3 entregue no Moodle.
--
-- Tabelas criadas pelo Django:
--   blog_post             (id, title, content, date)
--   blog_comment          (id, text, date, author_id, post_id)
--   blog_category         (id, name, description)
--   blog_post_categories  (id, post_id, category_id)

-- 1. Todos os posts, ordenados pela data, do mais recente para o mais antigo.
SELECT *
FROM blog_post
ORDER BY date DESC;

-- 2. Todos os comentários de um post com comentários (troque o 1 pelo id do post).
SELECT *
FROM blog_comment
WHERE post_id = 1;

-- 3. Comentários de um post com todas as colunas da tabela de comentários
--    (menos post_id), o título do post e a data dele renomeada para post_date.
SELECT c.id,
       c.text,
       c.date,
       c.author_id,
       p.title,
       p.date AS post_date
FROM blog_comment AS c
JOIN blog_post AS p ON p.id = c.post_id
WHERE c.post_id = 1;

-- 4. Todos os posts de uma categoria (Oficinas), com as colunas da tabela de
--    categorias e da tabela de posts.
SELECT cat.*,
       p.*
FROM blog_category AS cat
JOIN blog_post_categories AS pc ON pc.category_id = cat.id
JOIN blog_post AS p ON p.id = pc.post_id
WHERE cat.name = 'Oficinas';

-- 5. Todas as categorias que possuem dois ou mais posts.
SELECT cat.*,
       COUNT(pc.post_id) AS total_posts
FROM blog_category AS cat
JOIN blog_post_categories AS pc ON pc.category_id = cat.id
GROUP BY cat.id
HAVING COUNT(pc.post_id) >= 2;
