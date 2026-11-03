# Feature Specification: Núcleo de Convive (cuentas, pisos y tablón)

**Feature Branch**: `001-nucleo-convive`

**Created**: 2026-11-03

**Status**: Draft

**Input**: User description: "Núcleo común de Convive (SPECS.md, sección 2 y aclaraciones de la sección 4): app web para que los compañeros de piso organicen la convivencia. Registro e inicio de sesión, crear y unirse a un piso con código de invitación, ver el piso, expulsar, abandonar, regenerar código, y tablón de avisos."

## Clarifications

### Session 2026-11-03

- Q: ¿Al registrarse se pide también un nombre visible? → A: Sí, obligatorio (1–40 caracteres).
- Q: ¿Cuánto dura la sesión antes de tener que volver a iniciar sesión? → A: 24 horas, sin
  renovación.
- Q: ¿Qué pasa con los avisos de un miembro que abandona el piso o es expulsado? → A: Se borran
  todos sus avisos de ese piso.
- Q: ¿En qué idioma va la interfaz y los mensajes para la persona usuaria? → A: Español e inglés
  (español por defecto).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Crear cuenta e iniciar sesión (Priority: P1)

Un visitante se registra con su email y una contraseña y después inicia sesión para acceder a la
aplicación. Sin cuenta no puede hacer nada más.

**Why this priority**: Es la puerta de entrada; todas las demás historias exigen un usuario
identificado.

**Independent Test**: Registrar una cuenta, iniciar sesión con ella y comprobar que se obtiene
acceso; intentar entrar con credenciales erróneas y comprobar que se rechaza.

**Acceptance Scenarios**:

1. **Given** un visitante con un email no registrado, **When** se registra con un email válido,
   una contraseña de al menos 8 caracteres y un nombre de 1 a 40 caracteres, **Then** la cuenta
   se crea.
2. **Given** un email ya registrado, **When** otro visitante intenta registrarse con él,
   **Then** se rechaza con el error de conflicto `email_ya_registrado`.
3. **Given** un visitante, **When** se registra con una contraseña de menos de 8 caracteres, un
   email con formato no válido o sin nombre, **Then** se rechaza con un error de datos no válidos.
4. **Given** una cuenta existente, **When** el usuario inicia sesión con sus credenciales
   correctas, **Then** obtiene una sesión válida.
5. **Given** cualquier visitante, **When** inicia sesión con un email inexistente o una contraseña
   incorrecta, **Then** se rechaza con el mismo mensaje genérico en ambos casos, sin revelar si el
   email existe.

---

### User Story 2 - Crear un piso o unirse a uno (Priority: P1)

Un usuario sin piso crea uno (y pasa a ser su administrador) o se une a uno existente con el
código de invitación que le ha pasado un compañero.

**Why this priority**: Sin piso no hay convivencia que organizar; es el segundo paso
imprescindible del MVP.

**Independent Test**: Un usuario crea un piso y recibe un código; otro usuario se une con ese
código y ambos quedan en el mismo piso.

**Acceptance Scenarios**:

1. **Given** un usuario sin piso, **When** crea un piso con un nombre de 1 a 60 caracteres (y
   dirección opcional), **Then** el piso se crea con un código de invitación único de 8
   caracteres alfanuméricos y el usuario queda como su administrador.
2. **Given** un usuario sin piso, **When** intenta crear un piso sin nombre o con más de 60
   caracteres, **Then** se rechaza con un error de datos no válidos.
3. **Given** un usuario que ya pertenece a un piso, **When** intenta crear otro o unirse a otro,
   **Then** se rechaza con el error de conflicto `ya_tiene_piso`.
4. **Given** un usuario sin piso y un código válido, **When** se une con ese código, **Then**
   pasa a ser miembro (no administrador) de ese piso.
5. **Given** un usuario sin piso, **When** se une con un código que no existe, **Then** se
   rechaza con un error de recurso no encontrado.

---

### User Story 3 - Ver mi piso (Priority: P2)

Un miembro consulta el nombre de su piso, la lista de miembros y el rol de cada uno. El
administrador además ve el código de invitación para compartirlo.

**Why this priority**: Da sentido al piso como grupo y permite al administrador invitar a gente.

**Independent Test**: Con un piso de dos miembros, ambos consultan el piso; ambos ven nombre y
miembros, y solo el administrador ve el código.

**Acceptance Scenarios**:

1. **Given** un miembro de un piso, **When** consulta su piso, **Then** ve el nombre, la
   dirección (si existe), la lista de miembros y el rol de cada uno.
2. **Given** el administrador, **When** consulta su piso, **Then** ve además el código de
   invitación.
3. **Given** un miembro no administrador, **When** consulta su piso, **Then** el código de
   invitación no aparece.
4. **Given** un usuario sin piso, **When** intenta consultar su piso, **Then** se le indica que
   no pertenece a ningún piso (error de recurso no encontrado).

---

### User Story 4 - Tablón de avisos (Priority: P2)

Los miembros publican avisos cortos ("mañana viene el fontanero") en el tablón del piso, los
leen del más reciente al más antiguo y pueden borrar los suyos. El administrador puede borrar
cualquiera.

**Why this priority**: Es el valor principal frente a un grupo de mensajería caótico, pero
depende de tener piso.

**Independent Test**: Un miembro publica un aviso, otro miembro lo ve en el tablón; el autor lo
borra y desaparece; un tercer miembro no puede borrar avisos ajenos.

**Acceptance Scenarios**:

1. **Given** un miembro, **When** publica un aviso con texto de 1 a 280 caracteres, **Then** el
   aviso se guarda con su autor y fecha de publicación.
2. **Given** un miembro, **When** intenta publicar un aviso vacío o de más de 280 caracteres,
   **Then** se rechaza con un error de datos no válidos.
3. **Given** un piso con varios avisos, **When** un miembro consulta el tablón, **Then** ve
   todos los avisos de su piso ordenados del más reciente al más antiguo, con autor y fecha.
4. **Given** dos pisos distintos con avisos, **When** un miembro consulta el tablón, **Then**
   nunca ve avisos del otro piso.
5. **Given** un aviso, **When** lo borra su autor o el administrador, **Then** desaparece del
   tablón.
6. **Given** un aviso, **When** intenta borrarlo otro miembro que no es autor ni administrador,
   **Then** se rechaza con un error de permiso denegado.
7. **Given** un aviso de otro piso o inexistente, **When** un miembro intenta borrarlo,
   **Then** se rechaza con un error de recurso no encontrado.

---

### User Story 5 - Gestionar los miembros del piso (Priority: P3)

El administrador puede expulsar a un miembro y regenerar el código de invitación para invalidar
el anterior. Cualquier miembro puede abandonar el piso; si se va el administrador, el rol pasa
al miembro más antiguo.

**Why this priority**: Mantenimiento del grupo; necesario a medio plazo pero no para empezar a
usar la app.

**Independent Test**: En un piso de tres miembros, el administrador regenera el código (el viejo
deja de funcionar), expulsa a un miembro y luego abandona; el miembro restante pasa a ser
administrador.

**Acceptance Scenarios**:

1. **Given** el administrador y otro miembro del piso, **When** el administrador lo expulsa,
   **Then** ese usuario deja de pertenecer al piso, queda sin piso y sus avisos se borran
   del tablón.
2. **Given** un miembro no administrador, **When** intenta expulsar a alguien, **Then** se
   rechaza con un error de permiso denegado.
3. **Given** el administrador, **When** intenta expulsarse a sí mismo, **Then** se rechaza con
   un error de datos no válidos.
4. **Given** el administrador, **When** intenta expulsar a un usuario que no es miembro de su
   piso, **Then** se rechaza con un error de recurso no encontrado.
5. **Given** un miembro no administrador, **When** abandona el piso, **Then** deja de pertenecer
   a él, queda sin piso y sus avisos se borran del tablón.
6. **Given** el administrador de un piso con más miembros, **When** abandona el piso, **Then** el
   rol de administrador pasa al miembro que lleva más tiempo en el piso.
7. **Given** el administrador como único miembro, **When** abandona el piso, **Then** el piso se
   elimina junto con sus avisos.
8. **Given** el administrador, **When** regenera el código de invitación, **Then** se genera un
   código nuevo único y el anterior deja de servir para unirse.
9. **Given** un miembro no administrador, **When** intenta regenerar el código, **Then** se
   rechaza con un error de permiso denegado.

---

### Edge Cases

- Un usuario expulsado o que abandona el piso puede crear otro piso o unirse a otro después.
- Al irse un miembro (abandono o expulsión) se borran todos sus avisos de ese piso; los avisos
  de los demás no cambian.
- Dos personas intentando registrarse a la vez con el mismo email: solo una cuenta se crea.
- Un usuario expulsado que aún tiene la sesión abierta pierde el acceso a los datos del piso en
  su siguiente acción.
- El email se compara sin distinguir mayúsculas y minúsculas (`Ana@x.com` = `ana@x.com`).
- Un código de invitación recién regenerado nunca coincide con el de otro piso.
- Cualquier acción, salvo registro e inicio de sesión, sin sesión válida se rechaza con un error
  de no autenticado.

## Requirements *(mandatory)*

### Functional Requirements

**Cuentas**

- **FR-001**: El sistema MUST permitir registrarse con email, contraseña y nombre visible
  obligatorio (1–40 caracteres).
- **FR-002**: El sistema MUST rechazar emails con formato no válido o ya registrados
  (`email_ya_registrado`).
- **FR-003**: El sistema MUST exigir contraseñas de al menos 8 caracteres.
- **FR-004**: El sistema MUST almacenar las contraseñas de forma irreversible (nunca en claro).
- **FR-005**: El sistema MUST permitir iniciar sesión con email y contraseña y responder con un
  mensaje genérico idéntico ante email inexistente o contraseña incorrecta.
- **FR-006**: El sistema MUST exigir sesión válida para toda acción salvo registro e inicio de
  sesión. La sesión caduca a las 24 horas de iniciarse, sin renovación; caducada, se pide volver a
  iniciar sesión.

**Pisos y membresía**

- **FR-007**: Un usuario sin piso MUST poder crear un piso con nombre (1–60 caracteres) y
  dirección opcional; queda como su único administrador.
- **FR-008**: El sistema MUST generar para cada piso un código de invitación único de 8
  caracteres alfanuméricos, sin caducidad.
- **FR-009**: Un usuario sin piso MUST poder unirse a un piso con un código válido; un código
  inexistente se rechaza como no encontrado.
- **FR-010**: Un usuario MUST pertenecer como máximo a un piso a la vez; crear o unirse
  teniendo piso se rechaza con `ya_tiene_piso`.
- **FR-011**: Cada piso MUST tener exactamente un administrador mientras tenga miembros.
- **FR-012**: Un miembro MUST poder ver el nombre y dirección de su piso, sus miembros con su
  rol y fecha de incorporación; el código de invitación solo lo ve el administrador.
- **FR-013**: Solo el administrador MUST poder expulsar a un miembro; no puede expulsarse a sí
  mismo.
- **FR-014**: Cualquier miembro MUST poder abandonar el piso. Si es el administrador, el rol pasa
  al miembro más antiguo; si era el único miembro, el piso y sus avisos se eliminan. Al irse un
  miembro (abandono o expulsión) se borran todos los avisos que publicó en ese piso.
- **FR-015**: Solo el administrador MUST poder regenerar el código de invitación; el anterior
  deja de ser válido de inmediato.

**Tablón de avisos**

- **FR-016**: Un miembro MUST poder publicar avisos de 1 a 280 caracteres; se registran autor y
  fecha.
- **FR-017**: Un miembro MUST poder ver los avisos de su piso del más reciente al más antiguo.
- **FR-018**: Solo el autor de un aviso o el administrador MUST poder borrarlo. Los avisos no se
  pueden editar.

**Transversales**

- **FR-019**: Un usuario MUST ver y modificar únicamente datos de su propio piso; los recursos de
  otro piso se tratan como inexistentes.
- **FR-020**: Todos los errores MUST comunicarse con un código de error estable y legible por
  máquina y un mensaje para la persona usuaria, distinguiendo: datos no válidos, no autenticado,
  permiso denegado, no encontrado y conflicto.
- **FR-021**: Los datos MUST persistir entre reinicios de la aplicación.
- **FR-022**: La interfaz MUST redirigir a quien no tiene sesión a la pantalla de acceso, y a
  quien tiene sesión pero no piso a la pantalla de bienvenida (crear o unirse).
- **FR-023**: La interfaz MUST estar disponible en español e inglés, con español por defecto; la
  persona usuaria puede cambiar de idioma y la elección se recuerda en su dispositivo.
- **FR-024**: Los mensajes de error para la persona usuaria MUST mostrarse en el idioma elegido;
  los códigos de error son estables e independientes del idioma.

### Key Entities

- **Usuario**: persona con cuenta. Email único, nombre visible, credencial protegida, fecha de
  alta.
- **Piso**: grupo de convivencia. Nombre, dirección opcional, código de invitación único, fecha
  de creación.
- **Miembro**: pertenencia de un usuario a un piso. Rol (administrador o miembro) y fecha de
  incorporación. Un usuario tiene como máximo una.
- **Aviso**: mensaje corto del tablón de un piso. Texto, autor, fecha de publicación.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Una persona nueva puede registrarse, crear un piso y compartir el código en menos
  de 2 minutos.
- **SC-002**: Un compañero con el código puede registrarse y unirse al piso en menos de
  1 minuto.
- **SC-003**: El 100 % de los criterios de aceptación de este documento están cubiertos por
  pruebas automatizadas que pasan.
- **SC-004**: En ninguna prueba un usuario obtiene o modifica datos de un piso que no es el suyo.
- **SC-005**: Los datos (cuentas, pisos, avisos) se conservan tras detener y volver a arrancar la
  aplicación.
- **SC-006**: Un aviso publicado aparece en el tablón de los demás miembros la próxima vez que lo
  consultan, sin pasos adicionales.

## Assumptions

- El registro pide, además de email y contraseña, un nombre visible (el modelo de datos de
  SPECS.md lo incluye y hace falta para mostrar miembros y autores de avisos).
- El código de invitación usa letras mayúsculas y dígitos y se acepta sin distinguir mayúsculas
  y minúsculas al unirse.
- No existe cierre de sesión en servidor; al salir, el cliente descarta su credencial.
- El tablón muestra todos los avisos sin paginación (un piso tiene pocos avisos).
- Fuera de alcance: notificaciones push o email, chat en tiempo real, app móvil, recuperación de
  contraseña, pagos reales y el módulo de gastos (feature posterior).
