WITH films_with_ratings AS (
    SELECT
        film_id,
        title,
        release_date,
        price,
        rating,
        user_rating,
        CASE
            WHEN user_rating >= 4.5 THEN 'Excellent'
            WHEN user_rating >= 4 THEN 'Good'
            WHEN user_rating >= 3 THEN 'Average'
            ELSE 'Poor'
        END AS rating_category
    FROM
        {{ ref('films') }}
),

films_with_actors AS (
    SELECT
        f.film_id,
        f.title,
        STRING_AGG(a.actor_name, ', ') AS actors
    FROM
        {{ ref('films') }} AS f
    LEFT JOIN
        {{ ref('film_actors') }} AS fa ON f.film_id = fa.film_id
    LEFT JOIN
        {{ ref('actors') }} AS a ON fa.actor_id = a.actor_id
    GROUP BY
        f.film_id,
        f.title
)

SELECT
    fwr.*,
    fwa.actors
FROM films_with_ratings AS fwr
LEFT JOIN films_with_actors AS fwa ON fwr.film_id = fwa.film_id