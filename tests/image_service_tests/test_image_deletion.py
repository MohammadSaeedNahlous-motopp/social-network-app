def test_old_file_is_deleted_when_image_is_replaced(
    db,
    create_test_group,
    create_test_user,
    tmp_path,
):
    old_file = tmp_path / "old.jpg"
    new_file = tmp_path / "new.jpg"

    old_file.write_text("old image")
    new_file.write_text("new image")

    user = create_test_user()

    group = create_test_group(
        owner=user,
        background_img=str(old_file),
    )

    group.background_img = str(new_file)
    db.commit()

    assert not old_file.exists()
    assert new_file.exists()


def test_old_file_is_not_deleted_when_transaction_is_rolled_back(
    db,
    create_test_group,
    create_test_user,
    tmp_path,
):
    old_file = tmp_path / "old.jpg"
    new_file = tmp_path / "new.jpg"

    old_file.write_text("old image")
    new_file.write_text("new image")

    user = create_test_user()

    group = create_test_group(
        owner=user,
        background_img=str(old_file),
    )

    group.background_img = str(new_file)
    db.rollback()

    assert old_file.exists()
    assert new_file.exists()


def test_old_profile_image_is_deleted_when_replaced(
    db,
    create_test_group,
    create_test_user,
    tmp_path,
):
    old_file = tmp_path / "old_profile.jpg"
    new_file = tmp_path / "new_profile.jpg"

    old_file.write_text("old image")
    new_file.write_text("new image")

    user = create_test_user()

    group = create_test_group(
        owner=user,
        profile_img=str(old_file),
    )

    group.profile_img = str(new_file)
    db.commit()

    assert not old_file.exists()
    assert new_file.exists()


def test_changing_non_file_field_does_not_delete_image(
    db,
    create_test_group,
    create_test_user,
        
    tmp_path,
):
    image = tmp_path / "image.jpg"
    image.write_text("image")

    user = create_test_user()

    group = create_test_group(
        owner=user,
        background_img=str(image),
    )

    group.name = "New name"
    db.commit()

    assert image.exists()


def test_assigning_same_file_does_not_delete_it(
    db,
    create_test_group,
    create_test_user,
    tmp_path,
):
    image = tmp_path / "image.jpg"
    image.write_text("image")

    user = create_test_user()

    group = create_test_group(
        owner=user,
        background_img=str(image),
    )

    group.background_img = str(image)
    db.commit()

    assert image.exists()
