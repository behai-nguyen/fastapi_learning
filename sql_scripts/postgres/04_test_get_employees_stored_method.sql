/*
    To test:
	
	SET search_path TO employees;
    select * from get_employees('%nas%', '%AN');
*/

set search_path to employees;

drop function if exists get_employees;

create function get_employees( 
    pmLastName varchar(16), 
    pmFirstName varchar(14) 
)
returns table ( 
    emp_no integer,
	email varchar(255),
	password varchar(100),
    birth_date date,
    first_name varchar(14),
    last_name varchar(16),
    gender character(1),
    hire_date date 
)
language plpgsql
as $$
begin
  return query

  select * from employees e where (lower(e.last_name) like lower(pmLastName))
    and (lower(e.first_name) like lower(pmFirstName)) order by e.emp_no;
end;
$$