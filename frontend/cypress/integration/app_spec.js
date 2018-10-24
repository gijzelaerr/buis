describe("Django REST framework / React quickstart app", () => {
    const repository = {
        url: "https://github.com/gijzelaerr/spiel"
    };
    before(() => {
        cy.exec("npm run dev");
        cy.exec("npm run flush");
    });
    it("should be able to fill a web form", () => {
        cy.visit("/");
        cy
            .get('input[name="url"]')
            .type(repository.url)
            .should("have.value", repository.url);

        cy.get("form").submit();
    });

    it("should be able to see the table", () => {
        cy.visit("/");
        cy.get("tr").contains(`${repository.url}`);
    });
});
