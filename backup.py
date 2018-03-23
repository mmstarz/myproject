        file2 = request.files["file2"]
        file3 = request.files["file3"]
        file4 = request.files["file4"]

        image2 = file2.filename
        image3 = file3.filename
        image4 = file4.filename

        destination = "/".join([target, image2])
        file2.save(destination)
        db.execute("UPDATE production SET image2 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image2), productid=productid)
        destination = "/".join([target, image3])
        file3.save(destination)
        db.execute("UPDATE production SET image3 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image3), productid=productid)
        destination = "/".join([target, image4])
        file4.save(destination)
        db.execute("UPDATE production SET image4 = :filename WHERE id = :productid", filename="/static/images/{}/{}".format(productid, image4), productid=productid)