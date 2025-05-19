package src;

import io.github.bonigarcia.wdm.WebDriverManager;
import org.openqa.selenium.*;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.interactions.Actions;
import org.openqa.selenium.support.ui.*;

import java.time.Duration;
import java.util.NoSuchElementException;
import java.util.function.Function;

public class TaskManagerTest {
    public static void main(String[] args) {

        // Setup WebDriver
        WebDriverManager.chromedriver().setup();
        WebDriver driver = new ChromeDriver();
        driver.manage().window().maximize();

        // 1️⃣ Implicit Wait
        driver.manage().timeouts().implicitlyWait(Duration.ofSeconds(10));

        // Navigate to Application
        driver.get("http://localhost:8080"); // Replace with your actual URL

        // Handle alert if any
        try {
            WebDriverWait alertWait = new WebDriverWait(driver, Duration.ofSeconds(3));
            Alert alert = alertWait.until(ExpectedConditions.alertIsPresent());
            System.out.println("Alert: " + alert.getText());
            alert.accept();
        } catch (TimeoutException ignored) {}

        // 2️⃣ Login
        driver.findElement(By.id("email")).sendKeys("testuser@example.com");
        driver.findElement(By.id("password")).sendKeys("password123");
        driver.findElement(By.cssSelector("button.login-btn")).click();

        // 3️⃣ Explicit wait for task input
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("taskInput")));

        // 4️⃣ Add a task
        String taskName = "Finish Java Selenium Script";

        WebElement taskInput = driver.findElement(By.id("taskInput"));
        taskInput.sendKeys(taskName);

        // 5️⃣ Select class usage - set priority
        Select priorityDropdown = new Select(driver.findElement(By.id("taskPriority")));
        priorityDropdown.selectByVisibleText("High");

        driver.findElement(By.id("addTaskBtn")).click();

        // 6️⃣ Fluent Wait - confirm task added
        Wait<WebDriver> fluentWait = new FluentWait<>(driver)
                .withTimeout(Duration.ofSeconds(15))
                .pollingEvery(Duration.ofSeconds(2))
                .ignoring(NoSuchElementException.class);

        fluentWait.until(driver1 -> {
            WebElement taskList = driver.findElement(By.id("taskList"));
            return taskList.getText().contains(taskName);
        });

        System.out.println("✅ Task added: " + taskName);

        // 7️⃣ Delete the task
        WebElement deleteButton = wait.until(ExpectedConditions.elementToBeClickable(
                By.xpath("//li[contains(.,'" + taskName + "')]//button[contains(@class,'delete-btn')]")
        ));
        deleteButton.click();
        System.out.println("🗑️ Task deleted: " + taskName);

        fluentWait.until(driver1 -> {
            WebElement taskList = driver.findElement(By.id("taskList"));
            return !taskList.getText().contains(taskName);
        });

        // 8️⃣ Hover over logout (Actions class)
        Actions actions = new Actions(driver);
        WebElement logoutBtn = driver.findElement(By.className("logout-btn"));
        actions.moveToElement(logoutBtn).perform();
        System.out.println("🖱️ Hovered over Logout button.");
        logoutBtn.click();
        System.out.println("🚪 Logged out.");

        driver.quit();
    }
}
